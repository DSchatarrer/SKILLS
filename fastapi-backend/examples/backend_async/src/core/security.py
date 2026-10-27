"""Pure authentication/authorization dependencies: no cleanup or writes."""
from datetime import datetime, timezone
from http import HTTPStatus
from typing import Any
from fastapi import Depends, HTTPException, Query, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .settings import settings
from .manager_db_async import get_session
from .token_utils import verify_token
from .models.sessions import Sessions
from .models.users import Users


def _as_utc(value: datetime) -> datetime:
    """SQLite may return naive datetimes; data is assumed stored as UTC."""
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


async def require_secret(secret: str = Query(...)) -> None:
    if secret != settings.API_KEY:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Clave secreta incorrecta")


async def require_auth(
    request: Request,
    roles: list[str] | None = None,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Check JWT + session expiry and optionally an allowed role. Never delete."""
    token_cookie = request.cookies.get("X-Sync.Ref")
    if not token_cookie:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Falta la cookie de autenticación")

    try:
        payload = verify_token(token_cookie)
    except ValueError:
        # Avoid exposing token internals to callers.
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Token inválido o expirado") from None

    session_token = payload.get("sub")
    if not session_token:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Token sin identificador de sesión")

    saved = await session.scalar(select(Sessions).where(Sessions.token == session_token))
    if saved is None or saved.exp is None or _as_utc(saved.exp) <= datetime.now(timezone.utc):
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Sesión no encontrada o expirada")

    if not saved.usu:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Sesión inválida")

    if roles is not None:
        user = await session.scalar(select(Users).where(Users.usu == saved.usu))
        if user is None or user.role not in roles:
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Permisos insuficientes")

    return {"username": saved.usu, "uuid": session_token, "token_payload": payload}


def require_roles(*roles: str):
    """Use as Depends(require_roles('admin', 'medico')). Empty roles deny."""
    async def _dep(request: Request, session: AsyncSession = Depends(get_session)):
        return await require_auth(request, roles=list(roles), session=session)
    return _dep
