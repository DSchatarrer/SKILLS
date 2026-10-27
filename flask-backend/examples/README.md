# Ejemplos REALES de Flask: última versión del ZIP del usuario

**Origen exacto:** `flask-estructura-fastapi-tipado-corregido.zip` → `flask-main/backend_sync/`.
Todos los archivos originales de `backend_sync/` están reproducidos **byte por byte**, sin modificaciones ni snippets inventados. `source-manifest.json` registra las rutas, tamaños y SHA-256 para comprobar la integridad.

## Cómo leerlos (carga progresiva)

El agente debe abrir **solo los archivos necesarios** para la tarea y, cuando genere código, seguir estas convenciones, sin copiar la implementación completa de manera indiscriminada.

| Quiero implementar/revisar | Ejemplos originales a consultar |
| --- | --- |
| Inicialización de Flask, CORS y registro de Blueprints | [`backend_sync/src/main.py`](backend_sync/src/main.py), [`backend_sync/src/applications/home/router.py`](backend_sync/src/applications/home/router.py) |
| Engine, `sessionmaker`, contexto de transacciones y DI | [`backend_sync/src/core/manager_db.py`](backend_sync/src/core/manager_db.py) |
| Endpoint login, cookies, registro protegido, decoradores | [`backend_sync/src/applications/login/router.py`](backend_sync/src/applications/login/router.py) |
| Negocio de login, hash de contraseñas y commits | [`backend_sync/src/applications/login/controller.py`](backend_sync/src/applications/login/controller.py) |
| Peticiones y respuestas Marshmallow | [`backend_sync/src/applications/login/schemas.py`](backend_sync/src/applications/login/schemas.py), [`backend_sync/src/applications/users/schemas.py`](backend_sync/src/applications/users/schemas.py) |
| Auth, JWT, sesiones persistidas y autorización | [`backend_sync/src/core/security.py`](backend_sync/src/core/security.py) |
| Rutas protegidas y API key de compatibilidad | [`backend_sync/src/applications/users/router.py`](backend_sync/src/applications/users/router.py) |
| Modelos SQLAlchemy 2 y metadatos | [`backend_sync/src/core/models/base.py`](backend_sync/src/core/models/base.py), [`backend_sync/src/core/models/users.py`](backend_sync/src/core/models/users.py), [`backend_sync/src/core/models/sessions.py`](backend_sync/src/core/models/sessions.py) |
| Settings y env de ejemplo | [`backend_sync/src/core/settings.py`](backend_sync/src/core/settings.py), [`backend_sync/.env.example`](backend_sync/.env.example) |
| CLI, creación de admin, limpieza de sesiones | [`backend_sync/src/core/commands.py`](backend_sync/src/core/commands.py), [`backend_sync/src/core/session_cleanup.py`](backend_sync/src/core/session_cleanup.py), [`backend_sync/src/scripts/cleanup_expired_sessions.py`](backend_sync/src/scripts/cleanup_expired_sessions.py) |
| Migraciones Alembic reales | [`backend_sync/migrations/env.py`](backend_sync/migrations/env.py), [`backend_sync/migrations/versions/20261027_01_baseline.py`](backend_sync/migrations/versions/20261027_01_baseline.py) |
| Tests HTTP, autenticación y rol | [`backend_sync/tests/conftest.py`](backend_sync/tests/conftest.py), [`backend_sync/tests/test_auth.py`](backend_sync/tests/test_auth.py), [`backend_sync/tests/test_admin_cli.py`](backend_sync/tests/test_admin_cli.py) |
| Tests de sesiones SQLAlchemy | [`backend_sync/tests/test_database.py`](backend_sync/tests/test_database.py) |
| Dependencias y ejecución | [`backend_sync/requirements.txt`](backend_sync/requirements.txt), [`backend_sync/README.md`](backend_sync/README.md) |

## Política para agentes

1. **Prioriza el repositorio real** donde estés trabajando y consulta estos ejemplos solo como patrón. Si existe conflicto, el código del proyecto actual prevalece salvo petición explícita.
2. **No alteres `manager_db.py` por estilo** al seguir este patrón: conserva `class_=Session`, `expire_on_commit=False`, `pool_pre_ping=True`, `pool_recycle=1800`, `rollback()` explícito y el retorno `Generator[Session, None, None]`.
3. **No confundas un ejemplo fiel con una garantía de seguridad**. La compatibilidad `?apikey=` se conserva únicamente en rutas legadas: usa `X-API-Key` en nuevas rutas. Revisa CSRF y limitación de intentos antes de producción.
4. **No ejecutes migraciones, CLI que altere datos o `init_db()` por inspeccionar ejemplos**. Los archivos incluidos son referencias de código: no se importan ni ejecutan al instalar la skill.
5. Al resolver una tarea, indica qué archivos de estos ejemplos consultaste y cómo los adaptaste.

## Verificar que son los archivos del ZIP

`source-manifest.json` contiene SHA-256 de cada archivo copiado. Los tests de la skill validan el manifest contra los archivos incluidos. No se ha modificado contenido alguno del backend entregado.
