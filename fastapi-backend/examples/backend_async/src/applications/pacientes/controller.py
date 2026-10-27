"""Asynchronous CRUD for existing n_pacientes schema."""
from logging import Logger
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from core.utils import normalize_text
from .models import Pacientes
from .schemas import PacienteCreateModel, PacienteUpdateModel, PacienteResponseModel


class PacienteService:
    def __init__(self, session: AsyncSession, logger: Logger):
        self.session = session
        self.logger = logger

    async def get_all_paciente_names(self) -> dict:
        try:
            result = await self.session.execute(select(Pacientes.id, Pacientes.username))
            return {"nombres": [{"id": row.id, "username": row.username} for row in result.all()]}
        except OperationalError:
            self.logger.exception("Error de conexión al consultar pacientes")
            raise HTTPException(status_code=503, detail="Base de datos no disponible") from None
        except SQLAlchemyError:
            self.logger.exception("Error al consultar pacientes")
            raise HTTPException(status_code=500, detail="Error al consultar pacientes") from None

    async def create_paciente(self, data: PacienteCreateModel) -> PacienteResponseModel:
        paciente = Pacientes(username=normalize_text(data.username))
        try:
            self.session.add(paciente)
            await self.session.commit()
            await self.session.refresh(paciente)
        except IntegrityError:
            await self.session.rollback()
            raise HTTPException(status_code=409, detail="Ya existe un paciente con ese nombre") from None
        except SQLAlchemyError:
            await self.session.rollback()
            self.logger.exception("Error al crear paciente")
            raise HTTPException(status_code=500, detail="Error al crear paciente") from None
        return PacienteResponseModel.model_validate(paciente)

    async def update_paciente(self, paciente_id: int, data: PacienteUpdateModel) -> PacienteResponseModel:
        paciente = await self.session.get(Pacientes, paciente_id)
        if paciente is None:
            raise HTTPException(status_code=404, detail="Paciente no encontrado")
        changes = data.model_dump(exclude_unset=True)
        if "username" in changes and changes["username"] is not None:
            changes["username"] = normalize_text(changes["username"])
        for key, value in changes.items():
            setattr(paciente, key, value)
        try:
            await self.session.commit()
            await self.session.refresh(paciente)
        except IntegrityError:
            await self.session.rollback()
            raise HTTPException(status_code=409, detail="Nombre de paciente duplicado") from None
        except SQLAlchemyError:
            await self.session.rollback()
            self.logger.exception("Error al actualizar paciente")
            raise HTTPException(status_code=500, detail="Error al actualizar paciente") from None
        return PacienteResponseModel.model_validate(paciente)

    async def delete_paciente(self, paciente_id: int) -> dict[str, str]:
        paciente = await self.session.get(Pacientes, paciente_id)
        if paciente is None:
            raise HTTPException(status_code=404, detail="Paciente no encontrado")
        try:
            await self.session.delete(paciente)
            await self.session.commit()
        except SQLAlchemyError:
            await self.session.rollback()
            self.logger.exception("Error al eliminar paciente")
            raise HTTPException(status_code=500, detail="Error al eliminar paciente") from None
        return {"message": "Paciente eliminado correctamente."}
