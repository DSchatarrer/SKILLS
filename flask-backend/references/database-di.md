# SQLAlchemy 2 sync e inyección de Session: conservar el diseño aprobado

## Invariantes de `src/core/manager_db.py`

En el último ZIP la implementación seleccionada por el usuario ya es intencionalmente sencilla:

1. `configure_database(app)` construye `create_engine(app.config["SQLALCHEMY_DATABASE_URI"], pool_pre_ping=True, pool_recycle=1800)` **una vez por app**.
2. Construye `sessionmaker(bind=engine, class_=Session, expire_on_commit=False)` **una vez por app**.
3. Guarda `sqlalchemy_engine` y `session_factory` en `app.extensions`, sin singletons globales de conexiones.
4. `get_session_factory()` obtiene el factory desde `current_app.extensions`.
5. `@contextmanager def get_session() -> Generator[Session, None, None]` usa `with get_session_factory()() as db`, hace `yield db`; ante `BaseException`, `db.rollback(); raise`. El `with` cierra la sesión.
6. `@require_db_session` llama `with get_session()` e inyecta `db=db` con `functools.wraps`; **no ejecuta commit automático**.
7. `init_db` importa modelos y usa `Base.metadata.create_all(engine)` **solo bootstrap local**.

Este diseño es válido. No cambiarlo solo porque `sessionmaker` acepte `class_=Session` por defecto. El aviso tipográfico previo se arregló cambiando `Iterator[Session]` por `Generator[Session, None, None]`: `@contextmanager` sigue estando vigente.

## Ejemplo mínimo de contexto (ilustrativo)

```python
from collections.abc import Generator
from contextlib import contextmanager
from sqlalchemy.orm import Session

@contextmanager
def get_session() -> Generator[Session, None, None]:
    with get_session_factory()() as db:
        try:
            yield db
        except BaseException:
            db.rollback()
            raise
```

**No uses `yield` como dependencia FastAPI**: Flask usa un context manager invocado explícitamente por el decorador. Una `Session` nunca debe almacenarse en un global/`lru_cache`, reutilizarse entre requests ni compartirse entre hilos.

## Transacciones

- En operaciones de **lectura**, no hay razón para hacer commit. Rollback al salir sin commit de una transacción pendiente ocurre con `Session.close()`; el explícito se conserva por claridad ante fallo.
- En la política actual, `controller.login` y `controller.create_user` hacen `db.commit()` explícito. No añadir commits en `require_auth` ni en `get_session` ni al final del request.
- Para tareas CLI con unidad de trabajo cerrada, `with get_session_factory().begin() as db:` compromete al éxito y revierte al fallo. **No** mezclar ese patrón con `db.commit()` oculto.
- Después de un fallo de `flush()`/integridad, usa rollback antes de reutilizar la sesión; vuelve a lanzar o transforma en error de dominio en la frontera adecuada.
- Mantén la operación atómica: si hay varios cambios relacionados, controla commit/rollback como una unidad. Si una transacción abarca varias llamadas de controllers, no introduzcas commits prematuros.

## Engine y vida de app

No ejecutar `engine.dispose()` en `teardown_appcontext` porque Flask desmonta el contexto en cada petición; se perdería el pool. En los tests con apps creadas dinámicamente, tras el fixture se puede hacer `app.extensions["sqlalchemy_engine"].dispose()` explícito. Cada app de tests debe tener su propio Engine y BD aislada.

## Integridad y modelos

Usa SQLAlchemy 2 con `DeclarativeBase`, `Mapped`, `mapped_column`, `select`, `Session.get`, `Session.scalars`. Conserva los nombres `usuarios(usu,hash_pwd,role)` y `sesiones(token,usu,exp)` en el repositorio base. No confiar en comprobaciones previas a insertar para evitar carreras: capturar `IntegrityError` y manejar rollback en los flujos donde aplique.

SQLAlchemy oficial: https://docs.sqlalchemy.org/en/20/orm/session_basics.html ; https://docs.sqlalchemy.org/en/20/orm/session_api.html
