import json
from typing import Optional

from openai import OpenAI
from sqlalchemy.orm import Session

from app.config import settings
from app.models.property import Property
from app.models.soil_analysis import SoilAnalysis
from app.services.recommendation_service import calcular_metricas


def build_context_json(
    user_id: int, db: Session, property_id: Optional[int] = None
) -> str:
    query = (
        db.query(SoilAnalysis)
        .join(Property)
        .filter(Property.proprietario_id == user_id)
    )
    if property_id is not None:
        query = query.filter(SoilAnalysis.propriedade_id == property_id)
    query = query.order_by(SoilAnalysis.data_analise.asc())

    rows = []
    for a in query.all():
        m = calcular_metricas(a)
        row = {
            "prop": a.propriedade.nome,
            "d": a.data_analise.isoformat(),
            "ph": a.ph,
            "p": a.fosforo,
            "k": a.potassio,
            "mo": a.materia_organica,
            "ca": a.calcio,
            "mg": a.magnesio,
            "v": m.saturacao_bases,
            "score": m.score_saude,
        }
        row = {k: v for k, v in row.items() if v is not None}
        rows.append(row)

    return json.dumps(rows, ensure_ascii=False, separators=(",", ":"))


def chat(user_message: str, context_json: str) -> str:
    SYSTEM = """You are an expert Agricultural Informatics Assistant for Brazilian Cerrado agronomy.
Answer STRICTLY based on the JSON data in <USER_DATA>. Be precise with dates and numbers.
When comparing trends, cite exact values and dates.

<DATA_SCHEMA>
prop=property name, d=date, ph=pH(CaCl2), p=phosphorus(mg/dm³),
k=potassium(cmolc/dm³), mo=organic matter(%), ca=calcium, mg=magnesium,
v=base saturation V%, score=health score 0-100
</DATA_SCHEMA>

<USER_DATA>
{context}
</USER_DATA>""".format(context=context_json)

    client = OpenAI(
        api_key=settings.LLM_API_KEY,
        base_url=settings.LLM_API_BASE,
    )

    response = client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user_message},
        ],
    )
    return response.choices[0].message.content.strip()
