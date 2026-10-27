"""Behavior checks without async DB driver; fake adapter delegates to real SQLAlchemy SQLite."""
import importlib.util
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from core.models.base import Base
from core.models.users import Users
from core.models.sessions import Sessions
from core.session_cleanup import purge_expired_sessions


class SyncAdapter:
    """Only a test double for AsyncSession's awaited methods; NOT production code."""
    def __init__(self, session):
        self.session = session

    async def scalar(self, statement):
        return self.session.scalar(statement)

    async def execute(self, statement):
        return self.session.execute(statement)

    async def get(self, model, key):
        return self.session.get(model, key)

    async def rollback(self):
        self.session.rollback()


def load_auth_with_stubbed_external_modules(monkeypatch):
    fake_db = ModuleType('core.manager_db_async')
    fake_db.get_session = lambda: None
    fake_jwt = ModuleType('core.token_utils')
    fake_jwt.verify_token = lambda cookie: {'sub': cookie}
    monkeypatch.setitem(sys.modules, 'core.manager_db_async', fake_db)
    monkeypatch.setitem(sys.modules, 'core.token_utils', fake_jwt)
    path = Path(__file__).resolve().parents[1] / 'src' / 'core' / 'security.py'
    spec = importlib.util.spec_from_file_location('core._security_isolated_test', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def db():
    engine = create_engine('sqlite+pysqlite:///:memory:')
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()


@pytest.mark.asyncio
async def test_current_role_allowed_without_cleanup(monkeypatch, db):
    auth = load_auth_with_stubbed_external_modules(monkeypatch)
    now = datetime.now(timezone.utc)
    db.add_all([
        Users(usu='ANA', role='admin'),
        Sessions(token='active', usu='ANA', exp=now + timedelta(days=1)),
        Sessions(token='old', usu='ANA', exp=now - timedelta(days=1)),
    ])
    db.commit()
    request = SimpleNamespace(cookies={'X-Sync.Ref': 'active'})
    result = await auth.require_auth(request, ['admin'], SyncAdapter(db))
    assert result['username'] == 'ANA'
    assert db.get(Sessions, 'old') is not None


@pytest.mark.asyncio
async def test_expired_denied_without_cleanup(monkeypatch, db):
    auth = load_auth_with_stubbed_external_modules(monkeypatch)
    db.add_all([
        Users(usu='ANA', role='admin'),
        Sessions(token='old', usu='ANA', exp=datetime.now(timezone.utc) - timedelta(seconds=1)),
    ])
    db.commit()
    with pytest.raises(HTTPException) as error:
        await auth.require_auth(SimpleNamespace(cookies={'X-Sync.Ref': 'old'}), ['admin'], SyncAdapter(db))
    assert error.value.status_code == 401
    assert db.get(Sessions, 'old') is not None


@pytest.mark.asyncio
async def test_role_denied_but_not_deleted(monkeypatch, db):
    auth = load_auth_with_stubbed_external_modules(monkeypatch)
    db.add_all([
        Users(usu='ANA', role='medico'),
        Sessions(token='active', usu='ANA', exp=datetime.now(timezone.utc) + timedelta(days=1)),
    ])
    db.commit()
    with pytest.raises(HTTPException) as error:
        await auth.require_auth(SimpleNamespace(cookies={'X-Sync.Ref': 'active'}), ['admin'], SyncAdapter(db))
    assert error.value.status_code == 403
    assert db.get(Users, 'ANA') is not None


@pytest.mark.asyncio
async def test_cleanup_respects_transaction_rollback(db):
    now = datetime.now(timezone.utc)
    db.add_all([
        Sessions(token='old', usu='ANA', exp=now - timedelta(days=1)),
        Sessions(token='new', usu='ANA', exp=now + timedelta(days=1)),
    ])
    db.commit()
    assert await purge_expired_sessions(SyncAdapter(db), now=now) == 1
    db.rollback()
    assert db.get(Sessions, 'old') is not None
    assert await purge_expired_sessions(SyncAdapter(db), now=now) == 1
    db.commit()
    assert db.get(Sessions, 'old') is None
    assert db.get(Sessions, 'new') is not None
