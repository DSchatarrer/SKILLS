"""Database-portable error log upsert (no postgresql-specific insert)."""
from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from .models import Errores


class LogsService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def insert_error_log(
        self, message_id: str, location: str,
        buzon: str | None = None, error: str | None = None,
    ) -> dict[str, str]:
        if not location:
            raise HTTPException(status_code=400, detail="location es obligatorio")
        key = (message_id, location)
        # ORM upsert works on SQLite, PostgreSQL, MySQL without dialect INSERT.
        # A concurrent insert can race; retry the update after IntegrityError.
        for attempt in range(2):
            saved = await self.session.get(Errores, key)
            if saved is None:
                self.session.add(Errores(message_id=message_id, location=location,
                                        buzon=buzon, error=error))
            else:
                saved.buzon = buzon
                saved.error = error
                saved.created_at = datetime.now(timezone.utc)
            try:
                await self.session.commit()
                return {"message": "Error log registrado o actualizado exitosamente."}
            except IntegrityError:
                await self.session.rollback()
                if attempt == 1:
                    raise HTTPException(status_code=409, detail="Conflicto concurrente al guardar") from None
            except SQLAlchemyError:
                await self.session.rollback()
                raise HTTPException(status_code=500, detail="Error al guardar el registro") from None
        raise HTTPException(status_code=409, detail="Error al guardar el registro")
