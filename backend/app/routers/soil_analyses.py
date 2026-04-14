from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, selectinload

from app.core.deps import get_current_user
from app.database import get_db
from app.models.property import Property
from app.models.recommendation import Recommendation
from app.models.soil_analysis import SoilAnalysis
from app.models.user import User
from app.schemas.soil_analysis import SoilAnalysisCreate, SoilAnalysisResponse, SoilAnalysisUpdate
from app.services.recommendation_service import gerar_recomendacoes

router = APIRouter()


def _check_property_access(prop_id: int, db: Session, user: User) -> Property:
    prop = db.query(Property).filter(
        Property.id == prop_id, Property.proprietario_id == user.id
    ).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Propriedade não encontrada ou sem permissão")
    return prop


@router.get("/", response_model=List[SoilAnalysisResponse])
def list_analyses(
    propriedade_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = (
        db.query(SoilAnalysis)
        .join(Property)
        .filter(Property.proprietario_id == current_user.id)
        .options(selectinload(SoilAnalysis.recomendacoes))
    )
    if propriedade_id:
        query = query.filter(SoilAnalysis.propriedade_id == propriedade_id)
    return query.order_by(SoilAnalysis.data_analise.desc()).offset(skip).limit(limit).all()


@router.post("/", response_model=SoilAnalysisResponse, status_code=status.HTTP_201_CREATED)
def create_analysis(
    payload: SoilAnalysisCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _check_property_access(payload.propriedade_id, db, current_user)

    analysis = SoilAnalysis(**payload.model_dump())
    db.add(analysis)
    db.flush()  # obter o ID antes de gerar recomendações

    for rec_data in gerar_recomendacoes(analysis):
        rec = Recommendation(**rec_data, analise_id=analysis.id)
        db.add(rec)

    db.commit()
    db.refresh(analysis)
    return analysis


@router.get("/{analysis_id}", response_model=SoilAnalysisResponse)
def get_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    analysis = (
        db.query(SoilAnalysis)
        .join(Property)
        .filter(SoilAnalysis.id == analysis_id, Property.proprietario_id == current_user.id)
        .options(selectinload(SoilAnalysis.recomendacoes))
        .first()
    )
    if not analysis:
        raise HTTPException(status_code=404, detail="Análise não encontrada")
    return analysis


@router.put("/{analysis_id}", response_model=SoilAnalysisResponse)
def update_analysis(
    analysis_id: int,
    payload: SoilAnalysisUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    analysis = (
        db.query(SoilAnalysis)
        .join(Property)
        .filter(SoilAnalysis.id == analysis_id, Property.proprietario_id == current_user.id)
        .options(selectinload(SoilAnalysis.recomendacoes))
        .first()
    )
    if not analysis:
        raise HTTPException(status_code=404, detail="Análise não encontrada")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(analysis, field, value)

    # Regerar recomendações
    db.query(Recommendation).filter(Recommendation.analise_id == analysis_id).delete()
    for rec_data in gerar_recomendacoes(analysis):
        rec = Recommendation(**rec_data, analise_id=analysis.id)
        db.add(rec)

    db.commit()
    db.refresh(analysis)
    return analysis


@router.delete("/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    analysis = (
        db.query(SoilAnalysis)
        .join(Property)
        .filter(SoilAnalysis.id == analysis_id, Property.proprietario_id == current_user.id)
        .first()
    )
    if not analysis:
        raise HTTPException(status_code=404, detail="Análise não encontrada")
    db.delete(analysis)
    db.commit()
