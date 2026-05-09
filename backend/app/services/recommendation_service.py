import json
from dataclasses import dataclass, field
from typing import List, Optional

from openai import OpenAI

from app.config import settings
from app.models.recommendation import PriorityLevel
from app.models.soil_analysis import SoilAnalysis

# Faixas de referência para solos agrícolas brasileiros (Cerrado/Embrapa)
_PH_MIN, _PH_MAX, _PH_OTM = 5.5, 6.5, 6.0
_MO_MIN, _MO_OTM = 2.5, 3.5          # %
_P_MIN, _P_OTM = 10.0, 15.0          # mg/dm³
_K_MIN, _K_OTM = 0.15, 0.20          # cmolc/dm³
_CA_MIN, _CA_OTM = 2.0, 4.0          # cmolc/dm³
_MG_MIN, _MG_OTM = 0.5, 1.0          # cmolc/dm³
_V_ALVO = 65.0                        # % saturação de bases ideal


@dataclass
class SoilMetrics:
    soma_bases: Optional[float] = None        # SB = Ca + Mg + K (cmolc/dm³)
    h_al_estimado: Optional[float] = None     # acidez potencial estimada
    ctc: Optional[float] = None               # CTC = SB + H+Al (cmolc/dm³)
    saturacao_bases: Optional[float] = None   # V% = SB/CTC × 100
    necessidade_calagem: Optional[float] = None  # NC em t/ha (PRNT 80%)
    score_saude: float = 0.0                  # 0–100
    desvios: dict = field(default_factory=dict)  # {parametro: valor normalizado}


def _desvio_normalizado(atual: float, minimo: float, otimo: float, maximo: Optional[float] = None) -> float:
    """Retorna desvio normalizado: >0 = déficit, <0 = excesso, 0 = ideal."""
    if maximo is not None and atual > maximo:
        return -(atual - otimo) / otimo
    if atual < minimo:
        return (otimo - atual) / otimo
    return 0.0


def calcular_metricas(analise: SoilAnalysis) -> SoilMetrics:
    m = SoilMetrics()

    # Soma de Bases (SB)
    bases = [v for v in [analise.calcio, analise.magnesio, analise.potassio] if v is not None]
    if bases:
        m.soma_bases = round(sum(bases), 3)

    # Estimativa de H+Al a partir do pH (método empírico simplificado para Cerrado)
    # Baseado na correlação de Raij: quanto mais ácido, maior a acidez potencial
    if analise.ph is not None and m.soma_bases is not None:
        fator_acidez = max(0.05, (7.0 - analise.ph) / (analise.ph - 3.5))
        m.h_al_estimado = round(m.soma_bases * fator_acidez, 3)
        m.ctc = round(m.soma_bases + m.h_al_estimado, 3)
        m.saturacao_bases = round((m.soma_bases / m.ctc) * 100, 1) if m.ctc > 0 else None

        # Necessidade de Calagem: NC = (V2 - V1) × CTC / (10 × PRNT)
        if m.saturacao_bases is not None and m.saturacao_bases < _V_ALVO:
            prnt = 0.80
            m.necessidade_calagem = round(
                (_V_ALVO - m.saturacao_bases) * m.ctc / (10 * prnt * 100), 2
            )

    # Desvios normalizados por parâmetro
    if analise.ph is not None:
        m.desvios["ph"] = round(_desvio_normalizado(analise.ph, _PH_MIN, _PH_OTM, _PH_MAX), 3)
    if analise.materia_organica is not None:
        m.desvios["materia_organica"] = round(_desvio_normalizado(analise.materia_organica, _MO_MIN, _MO_OTM), 3)
    if analise.fosforo is not None:
        m.desvios["fosforo"] = round(_desvio_normalizado(analise.fosforo, _P_MIN, _P_OTM), 3)
    if analise.potassio is not None:
        m.desvios["potassio"] = round(_desvio_normalizado(analise.potassio, _K_MIN, _K_OTM), 3)
    if analise.calcio is not None:
        m.desvios["calcio"] = round(_desvio_normalizado(analise.calcio, _CA_MIN, _CA_OTM), 3)
    if analise.magnesio is not None:
        m.desvios["magnesio"] = round(_desvio_normalizado(analise.magnesio, _MG_MIN, _MG_OTM), 3)

    # Score de saúde do solo (100 = ideal, 0 = crítico)
    if m.desvios:
        media_desvios = sum(abs(d) for d in m.desvios.values()) / len(m.desvios)
        m.score_saude = round(max(0.0, 100.0 - media_desvios * 100.0), 1)

    return m


def _montar_contexto(analise: SoilAnalysis, m: SoilMetrics) -> dict:
    ctx: dict = {"parametros_medidos": {}, "metricas_calculadas": {}}

    if analise.ph is not None:
        ctx["parametros_medidos"]["pH"] = {
            "valor": analise.ph,
            "faixa_ideal": f"{_PH_MIN}–{_PH_MAX}",
            "desvio_normalizado": m.desvios.get("ph"),
        }
    if analise.materia_organica is not None:
        ctx["parametros_medidos"]["materia_organica"] = {
            "valor_pct": analise.materia_organica,
            "minimo_ideal": _MO_MIN,
            "desvio_normalizado": m.desvios.get("materia_organica"),
        }
    if analise.fosforo is not None:
        ctx["parametros_medidos"]["fosforo_mg_dm3"] = {
            "valor": analise.fosforo,
            "minimo_ideal": _P_MIN,
            "desvio_normalizado": m.desvios.get("fosforo"),
        }
    if analise.potassio is not None:
        ctx["parametros_medidos"]["potassio_cmolc_dm3"] = {
            "valor": analise.potassio,
            "minimo_ideal": _K_MIN,
            "desvio_normalizado": m.desvios.get("potassio"),
        }
    if analise.calcio is not None:
        ctx["parametros_medidos"]["calcio_cmolc_dm3"] = {
            "valor": analise.calcio,
            "minimo_ideal": _CA_MIN,
            "desvio_normalizado": m.desvios.get("calcio"),
        }
    if analise.magnesio is not None:
        ctx["parametros_medidos"]["magnesio_cmolc_dm3"] = {
            "valor": analise.magnesio,
            "minimo_ideal": _MG_MIN,
            "desvio_normalizado": m.desvios.get("magnesio"),
        }

    if m.soma_bases is not None:
        ctx["metricas_calculadas"]["soma_bases_cmolc_dm3"] = m.soma_bases
    if m.ctc is not None:
        ctx["metricas_calculadas"]["ctc_estimada_cmolc_dm3"] = m.ctc
    if m.saturacao_bases is not None:
        ctx["metricas_calculadas"]["saturacao_bases_V_pct"] = {
            "valor": m.saturacao_bases,
            "ideal": f"{_V_ALVO}%",
        }
    if m.necessidade_calagem is not None:
        ctx["metricas_calculadas"]["necessidade_calagem_t_ha"] = m.necessidade_calagem
    ctx["metricas_calculadas"]["score_saude_solo_0_100"] = m.score_saude

    if analise.observacoes:
        ctx["observacoes_produtor"] = analise.observacoes

    return ctx


_PROMPT_SISTEMA = """Você é um agrônomo especialista em fertilidade do solo brasileiro (solos tropicais/Cerrado).
Receberá dados de uma análise de solo com parâmetros medidos e métricas agronômicas já calculadas.

Retorne um objeto JSON com a chave "recomendacoes" contendo um array de objetos no formato:
{
  "recomendacoes": [
    {
      "tipo": "nome curto da recomendação (máx 60 caracteres)",
      "descricao": "descrição técnica e prática com doses, produtos e método de aplicação, citando os valores calculados",
      "prioridade": "alta" | "media" | "baixa"
    }
  ]
}

Regras de prioridade baseadas no desvio_normalizado:
- alta:  desvio > 0.40 ou múltiplos parâmetros críticos simultâneos
- media: desvio entre 0.15 e 0.40
- baixa: desvio < 0.15 ou solo em boas condições

Gere no máximo 5 recomendações, ordenadas da maior para a menor prioridade.
Se o solo estiver em boas condições, retorne uma única recomendação de manutenção com prioridade baixa."""


def gerar_recomendacoes(analise: SoilAnalysis) -> List[dict]:
    metricas = calcular_metricas(analise)
    contexto = _montar_contexto(analise, metricas)

    client = OpenAI(
        api_key=settings.LLM_API_KEY,
        base_url=settings.LLM_API_BASE,
    )

    prompt = (
        "Analise os dados abaixo e gere as recomendações agronômicas:\n\n"
        + json.dumps(contexto, ensure_ascii=False, indent=2)
    )

    response = client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=[
            {"role": "system", "content": _PROMPT_SISTEMA},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
    )
    raw = response.choices[0].message.content.strip()
    recomendacoes = json.loads(raw)["recomendacoes"]

    priority_map = {
        "alta": PriorityLevel.ALTA,
        "media": PriorityLevel.MEDIA,
        "baixa": PriorityLevel.BAIXA,
    }

    return [
        {
            "tipo": r["tipo"],
            "descricao": r["descricao"],
            "prioridade": priority_map.get(r.get("prioridade", "media").lower(), PriorityLevel.MEDIA),
        }
        for r in recomendacoes
    ]
