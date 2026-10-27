"""Patient routes; authorization still requires admin as in original."""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from core.manager_db_async import get_session
from core.security import require_roles
from .controller import PacienteService
from .schemas import (
    PacienteNombresResponseModel, PacienteCreateModel, PacienteUpdateModel,
    PacienteResponseModel,
)

paciente_router = APIRouter(
    prefix="/pacientes", tags=["pacientes"], dependencies=[Depends(require_roles("admin"))]
)


@paciente_router.get("/nombres", response_model=PacienteNombresResponseModel)
async def get_paciente_names(request: Request, session: AsyncSession = Depends(get_session)):
    return await PacienteService(session, request.app.state.logger).get_all_paciente_names()


@paciente_router.post("/add", response_model=PacienteResponseModel)
async def create_paciente(
    data: PacienteCreateModel, request: Request, session: AsyncSession = Depends(get_session)
):
    return await PacienteService(session, request.app.state.logger).create_paciente(data)


@paciente_router.put("/update/{paciente_id}", response_model=PacienteResponseModel)
async def update_paciente(
    paciente_id: int, data: PacienteUpdateModel, request: Request,
    session: AsyncSession = Depends(get_session),
):
    return await PacienteService(session, request.app.state.logger).update_paciente(paciente_id, data)


@paciente_router.delete("/remove/{paciente_id}")
async def delete_paciente(
    paciente_id: int, request: Request, session: AsyncSession = Depends(get_session),
):
    return await PacienteService(session, request.app.state.logger).delete_paciente(paciente_id)
