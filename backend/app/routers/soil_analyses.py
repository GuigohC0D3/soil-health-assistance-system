import csv
import io
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, selectinload

from app.core.deps import get_current_user
from app.database import get_db
from app.models.property import Property
from app.models.recommendation import Recommendation
from app.models.soil_analysis import SoilAnalysis
from app.models.user import User
from app.schemas.soil_analysis import SoilAnalysisCreate, SoilAnalysisResponse, SoilAnalysisUpdate
from app.services.recommendation_service import calcular_metricas, gerar_recomendacoes

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


@router.get("/export")
def export_analyses_csv(
    propriedade_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = (
        db.query(SoilAnalysis)
        .join(Property)
        .filter(Property.proprietario_id == current_user.id)
    )
    if propriedade_id:
        query = query.filter(SoilAnalysis.propriedade_id == propriedade_id)
    analyses = query.order_by(SoilAnalysis.data_analise.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "id_amostra", "data_analise", "propriedade_id",
        "ph", "materia_organica_%", "fosforo_mg_dm3",
        "potassio_cmolc", "calcio_cmolc", "magnesio_cmolc",
        "soma_bases", "ctc_estimada", "saturacao_bases_V%",
        "necessidade_calagem_t_ha", "score_saude",
    ])
    for a in analyses:
        m = calcular_metricas(a)
        writer.writerow([
            a.id_amostra,
            a.data_analise.isoformat(),
            a.propriedade_id,
            a.ph, a.materia_organica, a.fosforo,
            a.potassio, a.calcio, a.magnesio,
            m.soma_bases, m.ctc, m.saturacao_bases,
            m.necessidade_calagem, m.score_saude,
        ])

    output.seek(0)
    filename = f"analises-solo-{date.today().isoformat()}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


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


@router.get("/{analysis_id}/fertilizer-plan")
def get_fertilizer_plan(
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

    prop = db.query(Property).filter(Property.id == analysis.propriedade_id).first()
    area = prop.area_hectares or 1.0

    m = calcular_metricas(analysis)

    v1 = m.saturacao_bases or 0.0
    v2 = 70.0
    prnt = 0.90
    ctc = m.ctc or 0.0
    nc_t_ha = round(max(0.0, (v2 - v1) * ctc / (100 * prnt)), 2) if v1 < v2 else 0.0
    nc_total = round(nc_t_ha * area, 2)

    p = analysis.fosforo or 0.0
    if p < 4:
        p2o5_kg_ha = 120
    elif p < 10:
        p2o5_kg_ha = 80
    elif p < 20:
        p2o5_kg_ha = 40
    else:
        p2o5_kg_ha = 20

    ss_kg_ha = round(p2o5_kg_ha / 0.18, 1)
    st_kg_ha = round(p2o5_kg_ha / 0.45, 1)
    ss_total = round(ss_kg_ha * area, 1)
    st_total = round(st_kg_ha * area, 1)

    k = analysis.potassio or 0.0
    if k < 0.10:
        k2o_kg_ha = 100
    elif k < 0.20:
        k2o_kg_ha = 60
    else:
        k2o_kg_ha = 30

    kcl_kg_ha = round(k2o_kg_ha / 0.60, 1)
    kcl_total = round(kcl_kg_ha * area, 1)

    mo = analysis.materia_organica or 0.0
    if mo < 1.5:
        n_dose = "alta"
    elif mo < 2.5:
        n_dose = "media"
    else:
        n_dose = "baixa"

    p_cat = "deficiente" if p < 10 else ("baixo" if p < 20 else "manutenção")
    k_cat = "deficiente" if k < 0.10 else ("baixo" if k < 0.20 else "manutenção")

    return {
        "analysis_id": analysis_id,
        "propriedade_nome": prop.nome,
        "area_hectares": area,
        "calagem": {
            "v1_pct": round(v1, 1),
            "nc_t_ha": nc_t_ha,
            "nc_total_t": nc_total,
        },
        "fosfato": {
            "p2o5_kg_ha": p2o5_kg_ha,
            "superfosfato_simples_kg_ha": ss_kg_ha,
            "superfosfato_simples_total_kg": ss_total,
            "superfosfato_triplo_kg_ha": st_kg_ha,
            "superfosfato_triplo_total_kg": st_total,
            "categoria": p_cat,
        },
        "potassio": {
            "k2o_kg_ha": k2o_kg_ha,
            "kcl_kg_ha": kcl_kg_ha,
            "kcl_total_kg": kcl_total,
            "categoria": k_cat,
        },
        "nitrogenio": {
            "dose_recomendada": n_dose,
        },
    }
