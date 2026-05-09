from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models.property import Property
from app.models.soil_analysis import SoilAnalysis
from app.models.user import User
from app.services.recommendation_service import calcular_metricas
from app.services.simulation_service import simular_calagem

router = APIRouter()


class LimingRequest(BaseModel):
    analise_id: int
    dosagem_calcario: float = Field(..., ge=0.0, le=10.0)
    cultura: str


@router.post("/liming")
def simulate_liming(
    body: LimingRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    analise = (
        db.query(SoilAnalysis)
        .join(Property)
        .filter(
            SoilAnalysis.id == body.analise_id,
            Property.proprietario_id == current_user.id,
        )
        .first()
    )
    if not analise:
        raise HTTPException(status_code=404, detail="Análise não encontrada")

    metricas = calcular_metricas(analise)
    return simular_calagem(metricas, body.dosagem_calcario, body.cultura, analise)
