"""One engine + one async_sessionmaker for the process; per-request sessions."""
from collections.abc import AsyncIterator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from .settings import settings
from .models.base import Base

async_engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI_ASYNC,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=1800,
)

# Construct once, *outside* get_session(). A session itself is never shared.
SessionLocal = async_sessionmaker(async_engine, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency: close the session when its request finishes."""
    async with SessionLocal() as session:
        yield session


async def init_db() -> None:
    """Development-only table bootstrap; use Alembic for production migrations."""
    import core.models.sessions  # noqa: F401
    import core.models.users  # noqa: F401
    import applications.pacientes.models  # noqa: F401
    import applications.info_errores.models  # noqa: F401
    async with async_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
