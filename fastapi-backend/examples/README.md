# Ejemplos REALES de FastAPI: backend del ZIP proporcionado

**Fuente:** `fastapi-main.zip` → `fastapi-main/backend_async/`.
Los **36 archivos originales** de `backend_async/` se incluyen completos, conservando cada byte. Se adjunta también el `README.md` original de la raíz en [`source-root-README.md`](source-root-README.md). El manifiesto [`source-manifest.json`](source-manifest.json) contiene rutas, tamaños y hashes SHA-256 para comprobarlo.

**Licencia y permiso:** [`backend_async/LICENSE.md`](backend_async/LICENSE.md) atribuye el código a Iberdrola S.A. y prohíbe su copia o distribución sin permiso expreso. El código se ha incorporado a petición del usuario como material de referencia, **no para publicación, venta, redistribución ni como plantilla de código libre**. Comprueba que tienes los permisos correspondientes antes de compartir o instalar esta skill en terceros o repositorios públicos.

## Mapa rápido: abrir SOLO el código necesario

| Necesidad del agente | Ejemplo real del ZIP | Qué observar |
| --- | --- | --- |
| Entrypoint y ciclo de vida de FastAPI | [`src/main.py`](backend_async/src/main.py) | `create_app`, `asynccontextmanager`, lifespan, CORS, `include_router`, `root_path` |
| Engine y sesiones asíncronas | [`src/core/manager_db_async.py`](backend_async/src/core/manager_db_async.py) | `create_async_engine`, `async_sessionmaker`, `AsyncSession`, `Depends(get_session)` |
| Configuración de entorno | [`src/core/settings.py`](backend_async/src/core/settings.py) | `BaseSettings`, credenciales externas, URI async; nunca registrar secretos |
| Router con control de roles | [`src/applications/pacientes/router.py`](backend_async/src/applications/pacientes/router.py) | APIRouter + `Depends(require_roles("admin"))` + schemas |
| CRUD y transacciones async | [`src/applications/pacientes/controller.py`](backend_async/src/applications/pacientes/controller.py) | `select`, commits, errores HTTP, integridad |
| Modelos Pydantic | [`src/applications/pacientes/schemas.py`](backend_async/src/applications/pacientes/schemas.py) | Create, Update y Response; `exclude_unset` en updates |
| ORM SQLAlchemy de dominio | [`src/applications/pacientes/models.py`](backend_async/src/applications/pacientes/models.py) | `Mapped`, `mapped_column`, restricciones |
| Login y cookie | [`src/applications/login/router.py`](backend_async/src/applications/login/router.py) y [`controller.py`](backend_async/src/applications/login/controller.py) | Entrada, cookies y sesión persistida; **no imitar alta sin auth** |
| Login schemas | [`src/applications/login/schemas.py`](backend_async/src/applications/login/schemas.py) | Contratos de credenciales/roles |
| Autenticación y autorización | [`src/core/security.py`](backend_async/src/core/security.py) | JWT/roles, DB sesión, secreto legado en URL |
| Codificar/validar JWT | [`src/core/token_utils.py`](backend_async/src/core/token_utils.py) | Claims, expiración y gestión de errores |
| Tablas de usuarios/sesiones | [`src/core/models/users.py`](backend_async/src/core/models/users.py), [`sessions.py`](backend_async/src/core/models/sessions.py), [`base.py`](backend_async/src/core/models/base.py) | Esquema ORM |
| Logs de errores | [`src/applications/info_errores/controllers.py`](backend_async/src/applications/info_errores/controllers.py) y [`models.py`](backend_async/src/applications/info_errores/models.py) | Upsert y reintentos con integridad |
| Caducidad y limpieza | [`src/core/session_cleanup.py`](backend_async/src/core/session_cleanup.py), [`src/scripts/cleanup_expired_sessions.py`](backend_async/src/scripts/cleanup_expired_sessions.py) | Job separado de petición; commit propiedad del llamador |
| Tests async | [`tests/test_auth_and_cleanup_async.py`](backend_async/tests/test_auth_and_cleanup_async.py) | pytest-asyncio, expiración y limpieza |
| Tests de roles | [`tests/test_authorization_sync_adapter.py`](backend_async/tests/test_authorization_sync_adapter.py) | Adaptador de test; **no** usar adaptador síncrono en producción |
| Tests ORM | [`tests/test_models_sqlalchemy.py`](backend_async/tests/test_models_sqlalchemy.py) | Tablas y modelos; diferencias DB |
| Configuración de tests | [`tests/conftest.py`](backend_async/tests/conftest.py) | Aislamiento con valores de pruebas |
| Dependencias | [`requirements.txt`](backend_async/requirements.txt) y [`requirements-dev.txt`](backend_async/requirements-dev.txt) | Versiones del snapshot, no requisitos universales |

## Cómo utilizar los ejemplos al editar un repositorio

1. Revisa **primero el repositorio abierto**. El código del ZIP es una referencia, no sustituye al proyecto real.
2. Abre solo los 1–3 archivos del índice relacionados con el cambio, por ejemplo `router.py` + `controller.py` + `schemas.py` para un CRUD.
3. Comprueba su contrato exacto y conserva las convenciones pertinentes si el usuario quiere mantener esta arquitectura. No trasplantes código completo ni afirmes que se trata de una plantilla segura.
4. **Corrige antes de replicar:** la ruta `POST /login/alta-usuario` del ZIP admite crear usuarios y seleccionar roles sin autenticación; una ruta nueva nunca debe copiar ese comportamiento. Revisa también secretos en query, cookies, CSRF y CORS.
5. No ejecutes automáticamente el código de `examples/`, ni inicialices bases de datos o limpiezas; examínalo como texto.
6. Para verificar que estos archivos conservan el contenido de origen, ejecuta los tests incluidos en la skill; la comparación byte a byte con el ZIP se hizo durante el empaquetado.

## Limitaciones del código recibido

- El snapshot utiliza `src` como raíz importable (`uvicorn main:app --app-dir src`), no necesariamente el paquete `src.main`.
- En desarrollo `init_db()` crea tablas, pero staging/producción requieren migraciones revisadas; el ZIP no contiene Alembic.
- No incluye `.env.example` aunque el README original lo mencione. No generes valores reales de secretos a partir de los ejemplos.
- Los tests originales son material de referencia; compilar no equivale a ejecutar la aplicación y sus dependencias.
- Licencia incluida: no elimines ni cambies el copyright del material recibido.
