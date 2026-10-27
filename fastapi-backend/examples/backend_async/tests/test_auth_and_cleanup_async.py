"""Integration coverage: run with requirements-dev.txt installed."""
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
import pytest
import pytest_asyncio

pytest.importorskip('aiosqlite')
pytest.importorskip('jose')

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from core.models.base import Base
from core.models.users import Users
from core.models.sessions import Sessions
from core.security import require_auth
from core.session_cleanup import purge_expired_sessions


@pytest_asyncio.fixture
async def factory():
    engine = create_async_engine('sqlite+aiosqlite:///:memory:')
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield async_sessionmaker(engine, expire_on_commit=False)
    await engine.dispose()


def fake_request():
    return SimpleNamespace(cookies={'X-Sync.Ref': 'TEST-TOKEN'})


@pytest.mark.asyncio
async def test_permission_does_not_cleanup(monkeypatch, factory):
    import core.security as security
    monkeypatch.setattr(security, 'verify_token', lambda _: {'sub': 'TEST'})
    now = datetime.now(timezone.utc)
    async with factory() as session:
        session.add_all([
            Users(usu='ANA', role='admin'),
            Sessions(token='TEST', usu='ANA', exp=now + timedelta(hours=1)),
            Sessions(token='OLD', usu='ANA', exp=now - timedelta(days=1)),
        ])
        await session.commit()
        assert (await require_auth(fake_request(), ['admin'], session))['username'] == 'ANA'
        assert await session.get(Sessions, 'OLD') is not None  # NO write during auth
        with pytest.raises(HTTPException) as exc:
            await require_auth(fake_request(), ['medico'], session)
        assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_expired_denied_even_before_cleanup(monkeypatch, factory):
    import core.security as security
    monkeypatch.setattr(security, 'verify_token', lambda _: {'sub': 'OLD'})
    async with factory() as session:
        session.add_all([
            Users(usu='ANA', role='admin'),
            Sessions(token='OLD', usu='ANA', exp=datetime.now(timezone.utc) - timedelta(seconds=1)),
        ])
        await session.commit()
        with pytest.raises(HTTPException) as exc:
            await require_auth(fake_request(), ['admin'], session)
        assert exc.value.status_code == 401
        assert await session.get(Sessions, 'OLD') is not None


@pytest.mark.asyncio
async def test_cleanup_uses_separate_transaction(factory):
    now = datetime.now(timezone.utc)
    async with factory() as session:
        session.add_all([
            Sessions(token='OLD', usu='ANA', exp=now - timedelta(seconds=10)),
            Sessions(token='NEW', usu='ANA', exp=now + timedelta(seconds=10)),
        ])
        await session.commit()
    async with factory() as session:
        count = await purge_expired_sessions(session, now=now)
        assert count == 1
        await session.rollback()
    async with factory() as session:
        assert await session.get(Sessions, 'OLD') is not None
    async with factory.begin() as session:
        count = await purge_expired_sessions(session, now=now)
    assert count == 1
    async with factory() as session:
        assert await session.get(Sessions, 'OLD') is None
        assert await session.get(Sessions, 'NEW') is not None
