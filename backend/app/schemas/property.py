from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PropertyCreate(BaseModel):
    nome: str
    area_hectares: Optional[float] = None
    localizacao: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None


class PropertyUpdate(BaseModel):
    nome: Optional[str] = None
    area_hectares: Optional[float] = None
    localizacao: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None


class PropertyResponse(BaseModel):
    id: int
    nome: str
    area_hectares: Optional[float]
    localizacao: Optional[str]
    cidade: Optional[str]
    estado: Optional[str]
    proprietario_id: int
    criado_em: datetime

    model_config = {"from_attributes": True}
