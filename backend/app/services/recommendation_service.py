from typing import List

from app.models.recommendation import PriorityLevel
from app.models.soil_analysis import SoilAnalysis


def gerar_recomendacoes(analise: SoilAnalysis) -> List[dict]:
    """
    Gera recomendações de manejo baseadas nos valores da análise de solo.
    Utiliza heurísticas baseadas em faixas de referência para solos agrícolas.
    """
    recomendacoes = []

    # --- pH ---
    if analise.ph is not None:
        if analise.ph < 5.5:
            prioridade = PriorityLevel.ALTA if analise.ph < 5.0 else PriorityLevel.MEDIA
            recomendacoes.append({
                "tipo": "Correção de pH",
                "descricao": (
                    f"pH do solo está baixo ({analise.ph:.1f}). Solo ácido reduz a disponibilidade de nutrientes "
                    f"e prejudica o desenvolvimento radicular. Recomenda-se aplicação de calcário para elevar o "
                    f"pH para a faixa ideal (5.5–6.5). Calcular a necessidade de calagem (NC) com base na "
                    f"análise completa e cultura a ser implantada."
                ),
                "prioridade": prioridade,
            })
        elif analise.ph > 7.5:
            recomendacoes.append({
                "tipo": "Solo Alcalino",
                "descricao": (
                    f"pH do solo está alto ({analise.ph:.1f}). Solo alcalino pode causar deficiências de "
                    f"micronutrientes como ferro, manganês e zinco. Verificar necessidade de acidificação "
                    f"com enxofre elementar ou sulfato de amônio. Consultar engenheiro agrônomo."
                ),
                "prioridade": PriorityLevel.MEDIA,
            })

    # --- Matéria Orgânica ---
    if analise.materia_organica is not None:
        if analise.materia_organica < 2.5:
            prioridade = PriorityLevel.ALTA if analise.materia_organica < 1.5 else PriorityLevel.MEDIA
            recomendacoes.append({
                "tipo": "Matéria Orgânica Insuficiente",
                "descricao": (
                    f"Teor de matéria orgânica baixo ({analise.materia_organica:.1f}%). A MO é fundamental "
                    f"para a estrutura, retenção de água e atividade biológica do solo. Recomenda-se: "
                    f"incorporação de composto orgânico (20–30 t/ha), esterco curtido, adoção de plantio "
                    f"direto com manutenção de palhada e uso de adubos verdes."
                ),
                "prioridade": prioridade,
            })

    # --- Fósforo ---
    if analise.fosforo is not None:
        if analise.fosforo < 10:
            prioridade = PriorityLevel.ALTA if analise.fosforo < 5 else PriorityLevel.MEDIA
            recomendacoes.append({
                "tipo": "Deficiência de Fósforo",
                "descricao": (
                    f"Nível de fósforo baixo ({analise.fosforo:.1f} mg/dm³). O fósforo é essencial para "
                    f"o desenvolvimento radicular e floração. Realizar adubação fosfatada com superfosfato "
                    f"simples (18% P₂O₅) ou superfosfato triplo (41% P₂O₅). A dose deve ser calculada "
                    f"conforme a cultura e o método de extração usado na análise."
                ),
                "prioridade": prioridade,
            })

    # --- Potássio ---
    if analise.potassio is not None:
        if analise.potassio < 0.15:
            prioridade = PriorityLevel.ALTA if analise.potassio < 0.08 else PriorityLevel.MEDIA
            recomendacoes.append({
                "tipo": "Deficiência de Potássio",
                "descricao": (
                    f"Nível de potássio baixo ({analise.potassio:.2f} cmolc/dm³). O potássio regula o "
                    f"balanço hídrico da planta e a resistência a doenças. Realizar adubação potássica "
                    f"com cloreto de potássio – KCl (60% K₂O) ou sulfato de potássio – K₂SO₄ (50% K₂O) "
                    f"para culturas sensíveis ao cloro."
                ),
                "prioridade": prioridade,
            })

    # --- Cálcio ---
    if analise.calcio is not None:
        if analise.calcio < 2.0:
            recomendacoes.append({
                "tipo": "Deficiência de Cálcio",
                "descricao": (
                    f"Nível de cálcio baixo ({analise.calcio:.1f} cmolc/dm³). O cálcio é essencial para "
                    f"o desenvolvimento celular e qualidade de frutos. Aplicar calcário calcítico (CaCO₃) "
                    f"ou gesso agrícola (CaSO₄) para elevar os teores de cálcio no solo."
                ),
                "prioridade": PriorityLevel.MEDIA,
            })

    # --- Magnésio ---
    if analise.magnesio is not None:
        if analise.magnesio < 0.5:
            recomendacoes.append({
                "tipo": "Deficiência de Magnésio",
                "descricao": (
                    f"Nível de magnésio baixo ({analise.magnesio:.2f} cmolc/dm³). O magnésio faz parte "
                    f"da clorofila e é essencial para a fotossíntese. Aplicar calcário dolomítico "
                    f"(CaMg(CO₃)₂) para corrigir simultaneamente o pH e os teores de cálcio e magnésio."
                ),
                "prioridade": PriorityLevel.MEDIA,
            })

    # --- Solo em Degradação (múltiplos fatores críticos) ---
    fatores_criticos = sum([
        1 if (analise.ph is not None and analise.ph < 5.5) else 0,
        1 if (analise.materia_organica is not None and analise.materia_organica < 2.5) else 0,
        1 if (analise.fosforo is not None and analise.fosforo < 10) else 0,
        1 if (analise.potassio is not None and analise.potassio < 0.15) else 0,
    ])
    if fatores_criticos >= 3:
        recomendacoes.append({
            "tipo": "Solo em Processo de Degradação",
            "descricao": (
                "Múltiplos parâmetros abaixo do nível crítico indicam degradação da fertilidade. "
                "Recomenda-se urgentemente: adoção de cobertura vegetal permanente, implantação de "
                "rotação de culturas, plantio direto e programa integrado de recuperação da fertilidade "
                "com acompanhamento técnico especializado."
            ),
            "prioridade": PriorityLevel.ALTA,
        })

    # Solo em boas condições
    if not recomendacoes:
        recomendacoes.append({
            "tipo": "Solo em Boas Condições",
            "descricao": (
                "Os parâmetros analisados estão dentro das faixas consideradas ideais. "
                "Manter as práticas de manejo atuais e realizar análises periódicas (a cada 2 anos) "
                "para monitorar a evolução da fertilidade."
            ),
            "prioridade": PriorityLevel.BAIXA,
        })

    return recomendacoes
