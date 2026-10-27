# Testing, comandos Click, migraciones

Código auténtico: [`tests/conftest.py`](../examples/backend_async/tests/conftest.py), [`tests/test_auth.py`](../examples/backend_async/tests/test_auth.py), [`src/core/commands.py`](../examples/backend_async/src/core/commands.py), [`migrations/env.py`](../examples/backend_async/migrations/env.py).

**Pruebas:** Desde `backend_async/`, tras instalar `requirements-dev.txt`, usar `python -m pytest -q tests validation` y `python -m compileall -q src tests migrations validation`. `tests/` cubre HTTP, cookies, roles, 401/403/409, rollback/expiración y SQLite async; `validation/` contiene verificaciones offline de estructura/driver y no reemplaza los tests de integración. Para cambios SQL no triviales, añadir ejecución PostgreSQL real.

**CLI:** Click es síncrono en la referencia, y usa `asyncio.run` en `init-db`, `create-admin` y `cleanup-sessions` para ejecutar corutinas. **No** usar `asyncio.run()` dentro de vistas `async def`, donde ya existe un event loop. `async with factory.begin()` maneja transacciones/commit en operaciones CLI.

**Migraciones:** Alembic usa `AsyncEngine` y `await connection.run_sync(do_run_migrations)`, mientras scripts de versiones siguen utilizando `op.*` síncrono. `create_all` sirve para base nueva en desarrollo, no migraciones productivas. Antes de `upgrade`/`stamp`, revisar baseline, DB existente, backups y plan de rollback. No lanzar migraciones contra BD real sin autorización.

**Reportar:** indicar pruebas realmente ejecutadas y resultados, y aclarar ausencia de dependencias/datos reales. El ZIP original se validó estáticamente, pero no dispone de una confirmación de tests HTTP integrada en su distribución.
