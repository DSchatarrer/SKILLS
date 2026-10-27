"""Login HTTP routes, preserved paths and request schema."""
from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from core.manager_db_async import get_session
from .controller import LoginService
from .schemas import LoginRequest, UserCreateRequest

login_router = APIRouter(prefix="/login", tags=["login"])


@login_router.post("/")
async def login(
    credentials: LoginRequest, request: Request, response: Response,
    session: AsyncSession = Depends(get_session),
):
    return await LoginService(session, request.app.state.logger).login(
        response=response, username=credentials.usu, password=credentials.pwd
    )


@login_router.post("/alta-usuario")
async def create_user(
    user_data: UserCreateRequest, request: Request,
    session: AsyncSession = Depends(get_session),
):
    # IMPORTANT: This original route has no authorization. See README security warning.
    return await LoginService(session, request.app.state.logger).create_user(
        username=user_data.usu, password=user_data.pwd, role=user_data.role
    )
