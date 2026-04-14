from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models.property import Property
from app.models.recommendation import Recommendation
from app.models.soil_analysis import SoilAnalysis
from app.models.user import User
from app.schemas.recommendation import RecommendationResponse

router = APIRouter()


@router.get("/", response_model=List[RecommendationResponse])
def list_recommendations(
    propriedade_id: Optional[int] = Query(None),
    analise_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = (
        db.query(Recommendation)
        .join(SoilAnalysis)
        .join(Property)
        .filter(Property.proprietario_id == current_user.id)
    )
    if propriedade_id:
        query = query.filter(SoilAnalysis.propriedade_id == propriedade_id)
    if analise_id:
        query = query.filter(Recommendation.analise_id == analise_id)
    return query.order_by(Recommendation.criado_em.desc()).offset(skip).limit(limit).all()
