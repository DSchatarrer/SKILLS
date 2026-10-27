# Testing, migraciones y despliegue (Flask síncrono)

## Pruebas de app y BD

Conservar fixtures de `tests/conftest.py`: construir `Settings(_env_file=None, ...)`, usar `DATABASE_URL=sqlite+pysqlite:///<tmp_path>/test.sqlite`, `create_app(settings=..., test_config={"TESTING": True})`, inicializar tablas solo en fixture bajo `with app.app_context():`, cargar usuarios de prueba con `session_factory.begin()`, usar `app.test_client()` y disponer Engine al terminar el fixture. No conectar a BD productiva en tests.

Tests importantes ya presentes en el ZIP:

- GET `/`, GET `/health`, login inválido uniforme 401.
- Login válido y acceso con cookie + `X-API-Key` a `/users/users`, sin revelar JWT.
- Alta de usuario: sin cookie 401, rol `user` 403, rol admin 201, duplicado 409.
- Sesión caducada en DB produce 401 **sin borrar el registro**.
- CLI `cleanup-sessions` borra sesiones expiradas en transacción independiente.
- `get_session()` revierte `flush` ante excepción; limpieza respeta retención y rollback.
- Preservación de nombres de tablas y columnas SQL existentes.

Al añadir funcionalidades, incluir positivos, negativos, aislamiento entre dos instancias Flask, cancelaciones/excepciones, integridad, caducidad de cookie, no modificaciones en auth y tests de regressión de paths heredados. No afirmar que tests SQLite cubran particularidades de PostgreSQL, locks, transacciones o concurrencia.

## Comandos locales

Desde `backend_sync/`:

```bash
python -m venv .venv
python -m pip install -r requirements-dev.txt
python -m compileall -q src tests migrations
pytest -q
flask --app src.main:create_app routes
```

`flask routes` sirve para comprobar rutas **si** están instaladas las dependencias y configuradas variables/BD. Para ejecutar tests no revelar secretos de `.env`; usar fixture de settings explícitos. Ejecutar `flask --app src.main:create_app run` solo en desarrollo y cuando lo solicite el usuario.

## Migraciones Alembic

- Base **nueva**: `alembic upgrade head` solo contra destino aprobado.
- Base **existente**: hacer backup y comparar tablas/columnas; si coincide exactamente con baseline, `alembic stamp 20261027_01` tras revisión (no indiscriminadamente).
- Evolución: `alembic revision --autogenerate -m "..."`, revisar manualmente diff de tipos, índices, restricciones, nullability y defaults; verificar `upgrade` y reversión en copia aislada.
- Nunca usar `Base.metadata.create_all()` para modificar esquemas productivos ni aplicar `upgrade` destructivo sin autorización.

`migrations/env.py` de referencia obtiene URL con `get_settings().sqlalchemy_database_uri`, importa todos los modelos y usa `Base.metadata`; en online crea Engine aislado con `NullPool`, ejecuta y hace `dispose()`.

## Operación

No ejecutar limpieza de sesiones en request ni middleware. Programar `flask --app src.main:create_app cleanup-sessions --retention-days 7` fuera del ciclo HTTP si el usuario pide configurar mantenimiento. En producción preferir servidor WSGI apropiado y configuración externa; `app.run(debug=True)` solo desarrollo. Revisar headers/proxies HTTPS, supervisión de pool, métricas, logs sin secretos y rate limiting.

Referencias: https://flask.palletsprojects.com/en/stable/testing/ ; https://alembic.sqlalchemy.org/en/latest/autogenerate.html ; https://flask.palletsprojects.com/en/stable/deploying/
