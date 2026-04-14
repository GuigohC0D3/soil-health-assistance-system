from datetime import datetime

from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class SoilAnalysis(Base):
    __tablename__ = "analises_solo"

    id = Column(Integer, primary_key=True, index=True)
    id_amostra = Column(String(50), nullable=False)
    data_analise = Column(Date, nullable=False)
    ph = Column(Float)
    materia_organica = Column(Float)   # %
    fosforo = Column(Float)            # mg/dm³
    potassio = Column(Float)           # cmolc/dm³
    calcio = Column(Float)             # cmolc/dm³
    magnesio = Column(Float)           # cmolc/dm³
    observacoes = Column(Text)
    propriedade_id = Column(Integer, ForeignKey("propriedades.id"), nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    propriedade = relationship("Property", back_populates="analises")
    recomendacoes = relationship(
        "Recommendation", back_populates="analise", cascade="all, delete-orphan"
    )
