from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models.property import Property
from app.models.recommendation import PriorityLevel, Recommendation
from app.models.soil_analysis import SoilAnalysis
from app.models.user import User

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
