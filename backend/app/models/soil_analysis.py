from datetime import date, datetime
from typing import Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SoilAnalysis(Base):
    __tablename__ = "analises_solo"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    id_amostra: Mapped[str] = mapped_column(String(50))
    data_analise: Mapped[date]
    ph: Mapped[Optional[float]] = mapped_column(default=None)
    materia_organica: Mapped[Optional[float]] = mapped_column(default=None)  # %
    fosforo: Mapped[Optional[float]] = mapped_column(default=None)           # mg/dm³
    potassio: Mapped[Optional[float]] = mapped_column(default=None)          # cmolc/dm³
    calcio: Mapped[Optional[float]] = mapped_column(default=None)            # cmolc/dm³
    magnesio: Mapped[Optional[float]] = mapped_column(default=None)          # cmolc/dm³
    observacoes: Mapped[Optional[str]] = mapped_column(Text, default=None)
    propriedade_id: Mapped[int] = mapped_column(ForeignKey("propriedades.id"))
    criado_em: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    atualizado_em: Mapped[Optional[datetime]] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )

    propriedade: Mapped["Property"] = relationship("Property", back_populates="analises")  # type: ignore[name-defined]
    recomendacoes: Mapped[list["Recommendation"]] = relationship(  # type: ignore[name-defined]
        "Recommendation", back_populates="analise", cascade="all, delete-orphan"
    )
