# SQLAlchemy asíncrono y DI

Patrón literal: [`src/core/manager_db.py`](../examples/backend_async/src/core/manager_db.py). No reemplazarlo por una clase `DatabaseManager`/Flask-SQLAlchemy sin necesidad.

1. `configure_database(app)` configura `create_async_engine(..., pool_pre_ping=True, pool_recycle=1800, poolclass=NullPool)` y `async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)` en `app.extensions`. Reusar uno por instancia de aplicación.
2. `get_session_factory() -> async_sessionmaker[AsyncSession]` recupera la factoría desde `current_app`.
3. `@asynccontextmanager` sobre `get_session() -> AsyncGenerator[AsyncSession, None]`: `async with factory() as db`; `await db.rollback()` en excepción; **no commit implícito**; cierre garantizado.
4. `require_db_session` envuelve cada vista async e inyecta `db`. Controladores deciden `await db.commit()`; comandos CLI pueden emplear `async with factory.begin()`.
5. Base de datos: `await db.get(Model,key)`, `await db.execute(select(Model))`, `await db.flush()`, `await db.commit()`; `db.add(model)` **no** lleva await.
6. Un `AsyncSession` no se comparte entre tareas concurrentes (`asyncio.gather` precisa una sesión por tarea). Evitar cargas lazy que lancen I/O implícito sin await.
7. `NullPool` evita reutilizar conexiones entre loops diferentes en contexto Flask WSGI/CLI/tests. No optimizarlo ciegamente; medir solo si el despliegue es ASGI exclusivo y el ciclo de vida de connections lo permite.
8. `init_db()` ejecuta `await connection.run_sync(Base.metadata.create_all)` únicamente para bootstrap. `dispose_database(app)` requiere `await`; no cerrar el engine después de cada request.

`settings.py` transforma URL a `postgresql+asyncpg`/`sqlite+aiosqlite`, rechazando drivers no compatibles. No mezclar `create_engine()` o `sessionmaker()` sync con `AsyncSession`.

Fuente: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html .
