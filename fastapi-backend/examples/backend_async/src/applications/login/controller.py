"""Login business logic; async SQLAlchemy; preserves X-Sync.Ref cookie."""
from logging import Logger
from fastapi import HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from werkzeug.security import generate_password_hash, check_password_hash
from core.settings import settings
from core.utils import normalize_text
from core.session_manager import SessionManager
from core.token_utils import create_token
from core.models.users import Users


class LoginService:
    def __init__(self, session: AsyncSession, logger: Logger):
        self.session = session
        self.logger = logger
        self.session_manager = SessionManager(session, logger)

    async def login(self, response: Response, username: str, password: str) -> dict[str, str]:
        if not username or not password:
            raise HTTPException(status_code=400, detail="Faltan los datos de acceso")
        name = normalize_text(username)
        user = await self.get_user(name)
        if user is None or not user.hash_pwd or not check_password_hash(user.hash_pwd, password):
            # Same response regardless of account existence.
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales incorrectas")
        token = create_token()
        await self.session_manager.create_session(name, token)
        response.set_cookie(
            key="X-Sync.Ref", value=token, max_age=settings.TOKEN_SECONDS_EXP,
            httponly=True, secure=settings.ENVIRONMENT != "local", samesite="lax", path="/"
        )
        return {"message": "Login correcto"}

    async def get_user(self, username: str) -> Users | None:
        return await self.session.scalar(select(Users).where(Users.usu == username))

    async def create_user(self, username: str, password: str, role: str) -> dict[str, str]:
        name = normalize_text(username)
        if not name or not password or not role:
            raise HTTPException(status_code=400, detail="Faltan datos del usuario")
        if await self.get_user(name):
            raise HTTPException(status_code=409, detail="Ya existe un usuario con ese nombre")
        user = Users(usu=name, hash_pwd=generate_password_hash(password), role=role)
        try:
            self.session.add(user)
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise HTTPException(status_code=409, detail="Ya existe un usuario con ese nombre") from None
        except SQLAlchemyError:
            await self.session.rollback()
            self.logger.exception("Error al crear usuario")
            raise HTTPException(status_code=500, detail="Error al crear usuario") from None
        return {"message": f"Usuario '{name}' creado exitosamente."}
