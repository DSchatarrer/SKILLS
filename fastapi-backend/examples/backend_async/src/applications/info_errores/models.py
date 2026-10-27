"""Portable SQLAlchemy mapping of existing errores_logs table."""
from datetime import datetime
from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from core.models.base import Base


class Errores(Base):
    __tablename__ = "errores_logs"

    message_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    location: Mapped[str] = mapped_column(String(255), primary_key=True)
    buzon: Mapped[str | None] = mapped_column(String(255), nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=True
    )

    def __repr__(self) -> str:
        return f"Errores(message_id={self.message_id!r}, location={self.location!r})"
