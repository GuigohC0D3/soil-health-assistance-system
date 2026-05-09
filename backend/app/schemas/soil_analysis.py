from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel

from app.schemas.recommendation import RecommendationResponse


class SoilAnalysisCreate(BaseModel):
    id_amostra: str
    data_analise: date
    ph: Optional[float] = None
    materia_organica: Optional[float] = None
    fosforo: Optional[float] = None
    potassio: Optional[float] = None
    calcio: Optional[float] = None
    magnesio: Optional[float] = None
    teor_argila: Optional[float] = None
    cor_munsell: Optional[str] = None
    observacoes: Optional[str] = None
    propriedade_id: int


class SoilAnalysisUpdate(BaseModel):
    id_amostra: Optional[str] = None
    data_analise: Optional[date] = None
    ph: Optional[float] = None
    materia_organica: Optional[float] = None
    fosforo: Optional[float] = None
    potassio: Optional[float] = None
    calcio: Optional[float] = None
    magnesio: Optional[float] = None
    teor_argila: Optional[float] = None
    cor_munsell: Optional[str] = None
    observacoes: Optional[str] = None


class SoilAnalysisResponse(BaseModel):
    id: int
    id_amostra: str
    data_analise: date
    ph: Optional[float]
    materia_organica: Optional[float]
    fosforo: Optional[float]
    potassio: Optional[float]
    calcio: Optional[float]
    magnesio: Optional[float]
    teor_argila: Optional[float]
    cor_munsell: Optional[str]
    observacoes: Optional[str]
    propriedade_id: int
    criado_em: datetime
    recomendacoes: List[RecommendationResponse] = []

    model_config = {"from_attributes": True}
