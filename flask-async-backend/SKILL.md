---
name: flask-async-backend
description: Crear, mantener, refactorizar, auditar y probar backends Flask con vistas async def y SQLAlchemy 2 asíncrono (AsyncEngine, async_sessionmaker, AsyncSession), arquitectura backend_async/src/applications/core, Flask-Smorest, Marshmallow, JWT/cookies, Alembic y WsgiToAsgi/Hypercorn. Usar en proyectos Flask async o conversiones sync a async; no para Flask exclusivamente síncrono, FastAPI ni frontend.
---

# Flask Async Backend — Codex y OpenCode

Actúa como ingeniero de backend especializado en **Flask con lógica y persistencia asíncronas**. Prioriza **compatibilidad, seguridad, sesiones de vida corta, pruebas y modificaciones mínimas**. La skill incluye **46 archivos auténticos** del proyecto `flask-async-sqlalchemy-proyecto-completo.zip`, íntegros y verificables: consulta [examples/README.md](examples/README.md). Estos ejemplos son una **referencia de implementación**, no una orden de copiar vulnerabilidades o ajustes locales.

## Activación y límites

- Úsala para rutas `async def` de Flask-Smorest, `AsyncSession`, `AsyncEngine`, `async_sessionmaker`, controladores y decoradores asíncronos, auth, CLI, Alembic, tests, ASGI/WSGI y migración desde Flask síncrono a async.
- Para Flask **solo síncrono**, usa la skill `flask-backend`; para ASGI nativo, FastAPI o Quart, selecciona otra arquitectura/skill. No la actives por un cambio puramente frontend.
- **No confundas async I/O con un servidor ASGI nativo**: Flask continúa siendo WSGI y puede ejecutarse a través de `WsgiToAsgi`. Una vista async no aumenta por sí sola el número de peticiones concurrentes por worker WSGI. Leer [references/asgi-and-deployment.md](references/asgi-and-deployment.md).

## Procedimiento obligatorio

1. **Inspecciona el repositorio real**: versión de Flask y Flask-Smorest, `requirements`, `main.py`, `asgi.py`, modelos, Blueprints, rutas, middleware/decoradores, pool de conexiones, driver de base de datos, migraciones y tests. Consulta [references/repo-map.md](references/repo-map.md) y [el índice de ejemplos](examples/README.md). No inventes contratos.
2. **Respeta la organización existente**. Patrón del proyecto de referencia: `flask-async-main/backend_async/src/main.py`, `src/asgi.py`, `src/applications/<dominio>/{router,controller,schemas}.py`, `src/core/{manager_db,security,settings,models,commands,session_cleanup}.py`, `migrations/`, `tests/` y `validation/`. Si el proyecto difiere, no impongas un refactor no pedido. Leer [references/app-factory-routing.md](references/app-factory-routing.md).
3. **Una factoría por app y una sesión por operación/tarea**. Mantén `configure_database(app)` con `create_async_engine`, `async_sessionmaker(..., class_=AsyncSession, expire_on_commit=False)`, `app.extensions`, `NullPool` del ejemplo por los posibles múltiples event loops y `@asynccontextmanager` → `AsyncGenerator[AsyncSession, None]`. `get_session()` hace `await db.rollback()` al fallar; `require_db_session` inyecta `db`, **no realiza commit implícito**. Nunca compartas `AsyncSession` entre tareas concurrentes. Lee [references/async-database-di.md](references/async-database-di.md) y [el manager_db real](examples/backend_async/src/core/manager_db.py).
4. **Propaga async hasta los límites de I/O**. Para ORM usa `await db.get(...)`, `await db.execute(...)`, `await db.commit()`, `await db.rollback()` y `async with factory()`. No llames a métodos async sin `await`; no uses `asyncio.run()` dentro de vistas async. Mantén hashing costoso en `asyncio.to_thread` si el código original lo requiere. Un método sin I/O, como `UsersController.greet`, puede seguir siendo `def`.
5. **Separa responsabilidades y conserva el contrato**. Routers gestionan Flask HTTP/cookies/validación, controllers negocio+persistencia, `schemas.py` Marshmallow, `models/` tablas existentes, y `core/` infraestructura. En el proyecto de ejemplo, preserva `GET /`, `GET /health`, `POST /login/`, `POST /login/register`, `GET /users/users`, cookie `X-Sync.Ref`, modelos `usuarios` y `sesiones`. Usa los [routers originales](examples/backend_async/src/applications/login/router.py) y [controllers originales](examples/backend_async/src/applications/login/controller.py).
6. **Autorización y decoradores antes de ampliar rutas**. `@require_db_session` debe envolver `@require_auth()` y `@require_role(...)`; el registro requiere `admin`; `require_auth` consulta JWT, sesión activa y usuario con `AsyncSession` y no borra sesiones. `X-API-Key` es preferente; `?apikey=` se conserva **solo** como compatibilidad antigua y **no** debe añadirse en endpoints nuevos. Revisa CSRF para cookies, CORS con credenciales, rate limiting, validación de roles y expiraciones: la referencia no garantiza endurecimiento productivo. Leer [references/auth-security.md](references/auth-security.md).
7. **CLI, migraciones, ciclo de vida**. `create_app()` y los comandos Click son sync; **solo en comandos CLI** el ejemplo usa `asyncio.run()` para invocar corutinas. Usa `async with factory.begin()` para transacciones CLI, `await connection.run_sync(Base.metadata.create_all)` solo para bootstrap, y Alembic `env.py` async con `run_sync`. Jamás crear/migrar tablas o limpiar sesiones dentro de peticiones. En entornos ASGI/loops múltiples valida la política de pool y `engine.dispose()`. Leer [references/testing-migrations.md](references/testing-migrations.md) y [references/asgi-and-deployment.md](references/asgi-and-deployment.md).
8. **Verifica antes de concluir**. Compara rutas/status/cookies/roles y tablas; prueba errores 400/401/403/404/409, excepciones/rollback, expiración, comandos CLI y migraciones. Ejecuta si hay dependencias `python -m pytest -q tests validation` y `python -m compileall -q src tests migrations validation`; está permitido ejecutar validaciones puramente estáticas sin instalar paquetes. No afirmes tests HTTP/DB que no hayas ejecutado. Evita operaciones destructivas, migraciones de producción y gestión de secretos sin permiso.

## Guía de ejemplos REALES (leer solo el necesario)

- [examples/README.md](examples/README.md): índice completo de archivos y tareas; incluye procedencia y manifiesto SHA-256.
- [examples/backend_async/src/main.py](examples/backend_async/src/main.py): factoría Flask, configuración OpenAPI, registro Blueprints y CORS.
- [examples/backend_async/src/asgi.py](examples/backend_async/src/asgi.py): ASGI mediante `WsgiToAsgi`, no ASGI nativo.
- [examples/backend_async/src/core/manager_db.py](examples/backend_async/src/core/manager_db.py): `AsyncEngine`, `NullPool`, `async_sessionmaker`, inyección y rollback.
- [examples/backend_async/src/applications/login/router.py](examples/backend_async/src/applications/login/router.py) y [controller.py](examples/backend_async/src/applications/login/controller.py): login, registro, HTTP y `await`.
- [examples/backend_async/src/core/security.py](examples/backend_async/src/core/security.py): auth asíncrona, JWT/cookies y roles.
- [examples/backend_async/src/core/commands.py](examples/backend_async/src/core/commands.py) y [migrations/env.py](examples/backend_async/migrations/env.py): fronteras sync/async de CLI y migraciones.
- [examples/backend_async/tests/conftest.py](examples/backend_async/tests/conftest.py) y [tests/test_auth.py](examples/backend_async/tests/test_auth.py): fixtures y contratos.

Los ejemplos se copiaron **byte a byte**, incluso donde muestran comportamientos legados, y no sustituyen la inspección del repositorio de trabajo. `examples/source-manifest.json` permite comprobar su integridad. No pegues ni ejecutes código de los ejemplos a ciegas.

## Referencias a cargar bajo demanda

| Necesidad | Archivo |
| --- | --- |
| Archivo/ruta del proyecto y contratos existentes | [references/repo-map.md](references/repo-map.md) |
| Factoría, Flask-Smorest, Blueprints, Marshmallow y routing | [references/app-factory-routing.md](references/app-factory-routing.md) |
| AsyncSession, pool, contextos, transacciones y dependencias | [references/async-database-di.md](references/async-database-di.md) |
| Seguridad JWT, roles, cookies, CORS, sesiones persistidas | [references/auth-security.md](references/auth-security.md) |
| CLI, Alembic, tests async/sync y validación | [references/testing-migrations.md](references/testing-migrations.md) |
| Flask WSGI, adaptador ASGI, loops y despliegue | [references/asgi-and-deployment.md](references/asgi-and-deployment.md) |

## Scripts auxiliares

- `python scripts/audit_flask.py --root RUTA_BACKEND --format text`: inventario **estático, de solo lectura**; identifica rutas y posibles puntos de revisión, **no** es una auditoría de seguridad ni ejecuta Flask.
- `python scripts/install_skill.py --target both --scope user`: instala una copia global en `.agents/skills/flask-async-backend` visible para Codex y OpenCode; el instalador acepta `--scope project --project-root RUTA`, `--dry-run` y `--force`.

## Salida esperada

Indica **qué archivos cambian**, **qué contratos se preservan**, **qué pruebas se han ejecutado realmente**, los **riesgos pendientes** (WSGI/ASGI, CSRF, pooling, migraciones) y si hay dependencia del entorno.
