from fastapi import HTTPException
from openai import OpenAI

from app.config import settings
from app.services.recommendation_service import SoilMetrics

_LLM_TIMEOUT = 30.0


def simular_calagem(
    m: SoilMetrics, dosagem_calcario: float, cultura: str, analise
) -> dict:
    if m.ctc is None or m.saturacao_bases is None:
        raise HTTPException(
            status_code=422,
            detail="Dados insuficientes na análise para calcular a simulação (CTC ou saturação de bases ausentes).",
        )

    prnt = 0.80
    delta_v = (dosagem_calcario * 10 * prnt * 100) / m.ctc
    v2 = min(round(m.saturacao_bases + delta_v, 1), 100.0)
    ph2 = round(4.0 + 0.025 * v2, 1)
    ph1 = round(4.0 + 0.025 * m.saturacao_bases, 1)

    client = OpenAI(
        api_key=settings.LLM_API_KEY,
        base_url=settings.LLM_API_BASE,
        timeout=_LLM_TIMEOUT,
    )

    prompt = (
        f"A saturação de bases sobe de {m.saturacao_bases}% para {v2}%. "
        f"O pH estimado passa de {ph1} para {ph2}. "
        f"Cultura-alvo: {cultura}. "
        f"Em 3 frases, explique o benefício agronômico para {cultura} "
        f"no desenvolvimento radicular e na disponibilidade de fósforo em Latossolos do Cerrado. "
        f"Não especule além desses números. Responda em português."
    )

    try:
        response = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "Você é um agrônomo especialista em solos do Cerrado brasileiro.",
                },
                {"role": "user", "content": prompt},
            ],
        )
        narrativa = response.choices[0].message.content.strip()
    except Exception:
        narrativa = None

    return {
        "antes": {
            "v_pct": m.saturacao_bases,
            "ph_estimado": ph1,
            "necessidade_calagem": m.necessidade_calagem,
            "score_saude": m.score_saude,
        },
        "depois": {
            "v_pct_simulado": v2,
            "ph_simulado": ph2,
        },
        "narrativa": narrativa,
    }
