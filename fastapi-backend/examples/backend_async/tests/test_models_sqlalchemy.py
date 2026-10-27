"""Works without async drivers: verifies schema portability and original names."""
from sqlalchemy import create_engine, inspect, select
from sqlalchemy.orm import Session
from core.models.base import Base
from core.models.users import Users
from core.models.sessions import Sessions
from applications.pacientes.models import Pacientes
from applications.info_errores.models import Errores


def test_all_original_table_names_and_columns_sqlite():
    engine = create_engine('sqlite+pysqlite:///:memory:')
    Base.metadata.create_all(engine)
    insp = inspect(engine)
    assert set(insp.get_table_names()) == {'usuarios', 'sesiones', 'n_pacientes', 'errores_logs'}
    assert set(x['name'] for x in insp.get_columns('sesiones')) == {'token', 'usu', 'exp'}
    assert set(x['name'] for x in insp.get_columns('usuarios')) == {'usu', 'hash_pwd', 'role'}
    assert set(x['name'] for x in insp.get_columns('n_pacientes')) == {'id', 'username', 'fecha_creacion', 'created_modificacion'}
    assert set(x['name'] for x in insp.get_columns('errores_logs')) == {'message_id', 'location', 'buzon', 'error', 'created_at'}


def test_orm_crud_sqlite():
    engine = create_engine('sqlite+pysqlite:///:memory:')
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        s.add(Users(usu='ANA', hash_pwd='hashed', role='admin'))
        s.add(Pacientes(username='ANA'))
        s.add(Errores(message_id='m', location='l', error='err'))
        s.commit()
        assert s.scalar(select(Users).where(Users.role == 'admin')).usu == 'ANA'
        patient = s.scalar(select(Pacientes))
        assert patient.id == 1
        patient.username = 'BERTA'
        s.commit()
        assert s.get(Pacientes, 1).username == 'BERTA'


def test_no_sqlmodel_or_postgresql_specific_code():
    from pathlib import Path
    source_root = Path(__file__).resolve().parents[1] / 'src'
    for path in source_root.rglob('*.py'):
        source = path.read_text(encoding='utf8')
        assert 'from sqlmodel' not in source
        assert 'import sqlmodel' not in source
        assert 'sqlalchemy.dialects.postgresql' not in source
