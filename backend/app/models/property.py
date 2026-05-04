from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Property(Base):
    __tablename__ = "propriedades"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(150))
    area_hectares: Mapped[Optional[float]] = mapped_column(default=None)
    localizacao: Mapped[Optional[str]] = mapped_column(String(255), default=None)
    cidade: Mapped[Optional[str]] = mapped_column(String(100), default=None)
    estado: Mapped[Optional[str]] = mapped_column(String(2), default=None)
    proprietario_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    criado_em: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    atualizado_em: Mapped[Optional[datetime]] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )

    proprietario: Mapped["User"] = relationship("User", back_populates="propriedades")  # type: ignore[name-defined]
    analises: Mapped[list["SoilAnalysis"]] = relationship(  # type: ignore[name-defined]
        "SoilAnalysis", back_populates="propriedade", cascade="all, delete-orphan"
    )
