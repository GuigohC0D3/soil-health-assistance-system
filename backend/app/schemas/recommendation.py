from datetime import datetime

from pydantic import BaseModel

from app.models.recommendation import PriorityLevel


class RecommendationResponse(BaseModel):
    id: int
    tipo: str
    descricao: str
    prioridade: PriorityLevel
    analise_id: int
    criado_em: datetime

    model_config = {"from_attributes": True}
