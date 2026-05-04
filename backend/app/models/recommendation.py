import enum
from datetime import datetime

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PriorityLevel(str, enum.Enum):
    ALTA = "alta"
    MEDIA = "media"
    BAIXA = "baixa"


class Recommendation(Base):
    __tablename__ = "recomendacoes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    tipo: Mapped[str] = mapped_column(String(100))
    descricao: Mapped[str] = mapped_column(Text)
    prioridade: Mapped[PriorityLevel] = mapped_column(
        Enum(PriorityLevel, values_callable=lambda x: [e.value for e in x]),
        default=PriorityLevel.MEDIA,
    )
    analise_id: Mapped[int] = mapped_column(ForeignKey("analises_solo.id"))
    criado_em: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    analise: Mapped["SoilAnalysis"] = relationship("SoilAnalysis", back_populates="recomendacoes")  # type: ignore[name-defined]
