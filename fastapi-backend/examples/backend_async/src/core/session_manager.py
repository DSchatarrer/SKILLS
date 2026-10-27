"""Session *creation* service. Expired-session cleanup is a separate job."""
from logging import Logger
from sqlalchemy.ext.asyncio import AsyncSession
from .models.sessions import Sessions
from .token_utils import get_uuid_and_exp_from_token


class SessionManager:
    def __init__(self, session: AsyncSession, logger: Logger):
        self.session = session
        self.logger = logger

    async def create_session(self, username: str, token: str) -> Sessions:
        try:
            uuid, exp = get_uuid_and_exp_from_token(token)
            saved = Sessions(token=uuid, usu=username, exp=exp)
            self.session.add(saved)
            await self.session.commit()
            await self.session.refresh(saved)
            return saved
        except Exception:
            await self.session.rollback()
            self.logger.exception("Error al crear sesión")
            raise
