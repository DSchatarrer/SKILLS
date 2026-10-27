"""Portable SQLAlchemy 2.x mapping of existing n_pacientes table."""
from datetime import datetime
from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column
from core.models.base import Base


class Pacientes(Base):
    __tablename__ = "n_pacientes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(355), unique=True, index=True, nullable=False)
    fecha_creacion: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=True
    )
    created_modificacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"Pacientes(username={self.username!r}, fecha_creacion={self.fecha_creacion!r})"
