from datetime import date, timedelta
from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models.property import Property
from app.models.soil_analysis import SoilAnalysis
from app.models.user import User
from app.services.recommendation_service import calcular_metricas

router = APIRouter()


class AlertItem(BaseModel):
    tipo: str
    mensagem: str
    prioridade: str
    propriedade_id: int
    propriedade_nome: str
    analise_id: int | None = None


@router.get("/", response_model=List[AlertItem])
def get_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    properties = (
        db.query(Property)
        .filter(Property.proprietario_id == current_user.id)
        .all()
    )
    alerts: list[AlertItem] = []
    six_months_ago = date.today() - timedelta(days=180)

    for prop in properties:
        analyses = (
            db.query(SoilAnalysis)
            .filter(SoilAnalysis.propriedade_id == prop.id)
            .order_by(SoilAnalysis.data_analise.desc())
            .all()
        )

        if not analyses:
            alerts.append(AlertItem(
                tipo="sem_analise",
                mensagem=f"Propriedade '{prop.nome}' nunca teve análise de solo registrada.",
                prioridade="media",
                propriedade_id=prop.id,
                propriedade_nome=prop.nome,
            ))
            continue

        latest = analyses[0]

        if latest.data_analise < six_months_ago:
            alerts.append(AlertItem(
                tipo="sem_analise_recente",
                mensagem=f"Propriedade '{prop.nome}' sem análise há mais de 6 meses.",
                prioridade="media",
                propriedade_id=prop.id,
                propriedade_nome=prop.nome,
                analise_id=latest.id,
            ))

        if latest.ph is not None and latest.ph < 5.0:
            alerts.append(AlertItem(
                tipo="ph_critico",
                mensagem=f"pH crítico ({latest.ph}) em '{prop.nome}'. Calagem urgente necessária.",
                prioridade="alta",
                propriedade_id=prop.id,
                propriedade_nome=prop.nome,
                analise_id=latest.id,
            ))

        m = calcular_metricas(latest)

        if m.saturacao_bases is not None and m.saturacao_bases < 40.0:
            alerts.append(AlertItem(
                tipo="v_baixo",
                mensagem=f"Saturação de bases V%={m.saturacao_bases:.1f}% abaixo do crítico em '{prop.nome}'.",
                prioridade="alta",
                propriedade_id=prop.id,
                propriedade_nome=prop.nome,
                analise_id=latest.id,
            ))

        if m.score_saude < 40:
            alerts.append(AlertItem(
                tipo="score_critico",
                mensagem=f"Score de saúde crítico ({m.score_saude}/100) em '{prop.nome}'.",
                prioridade="alta",
                propriedade_id=prop.id,
                propriedade_nome=prop.nome,
                analise_id=latest.id,
            ))

    alerts.sort(key=lambda a: 0 if a.prioridade == "alta" else 1)
    return alerts
