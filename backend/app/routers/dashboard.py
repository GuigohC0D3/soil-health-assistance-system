from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models.property import Property
from app.models.recommendation import PriorityLevel, Recommendation
from app.models.soil_analysis import SoilAnalysis
from app.models.user import User
from app.services.recommendation_service import calcular_metricas

router = APIRouter()


@router.get("/stats")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    properties_count = (
        db.query(Property)
        .filter(Property.proprietario_id == current_user.id)
        .count()
    )

    analyses_count = (
        db.query(SoilAnalysis)
        .join(Property)
        .filter(Property.proprietario_id == current_user.id)
        .count()
    )

    recommendations_count = (
        db.query(Recommendation)
        .join(SoilAnalysis)
        .join(Property)
        .filter(Property.proprietario_id == current_user.id)
        .count()
    )

    critical_count = (
        db.query(Recommendation)
        .join(SoilAnalysis)
        .join(Property)
        .filter(
            Property.proprietario_id == current_user.id,
            Recommendation.prioridade == PriorityLevel.ALTA,
        )
        .count()
    )

    return {
        "properties": properties_count,
        "analyses": analyses_count,
        "recommendations": recommendations_count,
        "critical": critical_count,
    }


@router.get("/trends")
def get_dashboard_trends(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    properties = (
        db.query(Property)
        .filter(Property.proprietario_id == current_user.id)
        .all()
    )

    prop_scores = []
    most_recent_prop_id = None
    most_recent_date_str = None

    for prop in properties:
        latest = (
            db.query(SoilAnalysis)
            .filter(SoilAnalysis.propriedade_id == prop.id)
            .order_by(SoilAnalysis.data_analise.desc())
            .first()
        )
        if latest:
            m = calcular_metricas(latest)
            date_str = latest.data_analise.isoformat()
            prop_scores.append({
                "propriedade_id": prop.id,
                "nome": prop.nome,
                "score": m.score_saude,
                "ultima_analise": date_str,
            })
            if most_recent_date_str is None or date_str > most_recent_date_str:
                most_recent_date_str = date_str
                most_recent_prop_id = prop.id

    prop_scores.sort(key=lambda x: x["score"], reverse=True)
    top3 = prop_scores[:3]

    ph_trend = []
    if most_recent_prop_id:
        recent_analyses = (
            db.query(SoilAnalysis)
            .filter(SoilAnalysis.propriedade_id == most_recent_prop_id)
            .order_by(SoilAnalysis.data_analise.asc())
            .limit(6)
            .all()
        )
        ph_trend = [
            {
                "data": a.data_analise.isoformat(),
                "ph": a.ph,
                "id_amostra": a.id_amostra,
            }
            for a in recent_analyses
            if a.ph is not None
        ]

    return {
        "top3_propriedades": top3,
        "ph_trend": ph_trend,
        "ph_trend_prop_id": most_recent_prop_id,
    }
