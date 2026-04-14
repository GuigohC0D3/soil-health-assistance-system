import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class PriorityLevel(str, enum.Enum):
    ALTA = "alta"
    MEDIA = "media"
    BAIXA = "baixa"


class Recommendation(Base):
    __tablename__ = "recomendacoes"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(100), nullable=False)
    descricao = Column(Text, nullable=False)
    prioridade = Column(Enum(PriorityLevel, values_callable=lambda x: [e.value for e in x]), default=PriorityLevel.MEDIA, nullable=False)
    analise_id = Column(Integer, ForeignKey("analises_solo.id"), nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)

    analise = relationship("SoilAnalysis", back_populates="recomendacoes")
