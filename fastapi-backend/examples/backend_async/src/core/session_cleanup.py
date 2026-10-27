"""Explicit cleanup service; NOT called from require_auth / require_roles."""
from datetime import datetime, timezone
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from .models.sessions import Sessions


async def purge_expired_sessions(session: AsyncSession, *, now: datetime | None = None) -> int:
    """Delete strictly expired sessions using caller-owned transaction.

    The caller decides when to commit/rollback. Validating a session never
    depends on when this cleanup job last ran.
    """
    cutoff = now or datetime.now(timezone.utc)
    if cutoff.tzinfo is None:
        raise ValueError("now must be timezone-aware")
    result = await session.execute(delete(Sessions).where(Sessions.exp < cutoff))
    return result.rowcount or 0
