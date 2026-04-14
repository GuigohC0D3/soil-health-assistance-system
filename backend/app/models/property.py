from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Property(Base):
    __tablename__ = "propriedades"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(150), nullable=False)
    area_hectares = Column(Float)
    localizacao = Column(String(255))
    cidade = Column(String(100))
    estado = Column(String(2))
    proprietario_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    proprietario = relationship("User", back_populates="propriedades")
    analises = relationship("SoilAnalysis", back_populates="propriedade", cascade="all, delete-orphan")
