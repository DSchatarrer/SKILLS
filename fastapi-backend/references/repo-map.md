# Mapa del backend de referencia (ZIP `fastapi-main.zip`)

Este archivo describe una **instantánea** del proyecto proporcionado por el usuario, no las versiones actuales de todas las bibliotecas. La fuente incluye `backend_async/LICENSE.md`, que restringe copia/distribución: **esta edición incorpora copias literales del código únicamente porque el usuario las ha solicitado**, pero **ello no otorga permiso para compartir ni redistribuir**. El índice está en [examples/README.md](../examples/README.md) y la licencia original se conserva en `examples/backend_async/LICENSE.md`. No presupongas que la fuente está instalada en el proyecto actual.

## Entorno y estilo observados

- Directorio: `fastapi-main/backend_async/` dentro del ZIP; al extraer normalmente `backend_async/`.
- Dependencias en `backend_async/requirements.txt`: FastAPI 0.115.12; Uvicorn 0.34.2; SQLAlchemy 2.0.40; asyncpg 0.30.0; `pydantic-settings` 2.x; `python-jose` 3.4.0; Werkzeug 3.1.3; `aiosqlite`; entre otras. **Son versiones del snapshot**, no recomendación de usar esas versiones siempre.
- Arranque desde `backend_async/`: `uvicorn main:app --app-dir src --reload`. Configuración por `.env` y `core.settings.Settings` (Pydantic Settings). Variables obligatorias `FASTAPI_SECRET_KEY`, `JWT_SECRET_KEY`, `API_KEY` y URL de base de datos; alternativa `DATABASE_URL` o `DATASOURCE_*` para compatibilidad.
- Enrutado y modelos bajo `src/`; imports estilo `from core...` y `from applications...` con `src` en `PYTHONPATH`/`--app-dir`.
- `src/main.py`: factoría `create_app()` + `lifespan`; registra routers `login` y `pacientes`, logger y CORS; `root_path="/nutricion"`, `openapi_url="/openapi.json"`, `docs_url="/docs"`. `root_path` no cambia mágicamente el path de la ruta en la app; examinar proxy/despliegue.
- `src/core/manager_db_async.py`: `create_async_engine`, `async_sessionmaker(expire_on_commit=False)`, `get_session()` con `async with`, `init_db()` solo en entorno `local` llamado desde lifespan.
- Modelos ORM de SQLAlchemy 2.x con una `DeclarativeBase` común en `src/core/models/base.py`.

## Rutas y paquetes

| Ubicación | Responsabilidad/contrato del snapshot |
| --- | --- |
| `src/applications/login/router.py` | `POST /login/` recibe `usu` + `pwd`; `POST /login/alta-usuario` recibe `usu`, `pwd`, `role` |
| `src/applications/login/controller.py` | Busca usuario y verifica hash; crea sesión JWT + DB, escribe cookie `X-Sync.Ref`; creación de usuarios |
| `src/applications/login/schemas.py` | Schemas Pydantic v2 de login/alta |
| `src/applications/pacientes/router.py` | `GET /pacientes/nombres`, `POST /pacientes/add`, `PUT /pacientes/update/{paciente_id}`, `DELETE /pacientes/remove/{paciente_id}`; router requiere rol `admin` |
| `src/applications/pacientes/controller.py` | CRUD async de pacientes, manejo de IntegrityError y transacciones |
| `src/applications/pacientes/models.py` | Tabla `n_pacientes`; PK `id`, `username` único, fechas |
| `src/applications/pacientes/schemas.py` | Create/Update/Response y lista de nombres |
| `src/applications/info_errores/controllers.py` | Servicio `LogsService`, upsert ORM con reintento limitado ante integridad; requiere considerar carreras |
| `src/applications/info_errores/models.py` | Tabla `errores_logs`, PK compuesta `message_id`, `location` |
| `src/core/models/users.py` | Tabla `usuarios`: `usu`, `hash_pwd`, `role` |
| `src/core/models/sessions.py` | Tabla `sesiones`: `token`, `usu`, `exp` |
| `src/core/security.py` | `require_auth`, `require_roles`, `require_secret` |
| `src/core/token_utils.py` | Creación y validación JWT con `sub` aleatorio y `exp` |
| `src/core/session_cleanup.py` | `purge_expired_sessions` sin commit: transacción gestionada por llamador |
| `src/scripts/cleanup_expired_sessions.py` | CLI con su propia sesión; se programa fuera del ciclo de peticiones |

## Advertencias de diseño: no copiar ciegamente

1. **Vulnerabilidad crítica en alta:** `POST /login/alta-usuario` no exige autenticación y permite seleccionar `role` (ejemplo del schema: `admin`). Se conserva por compatibilidad de origen, pero no debe exponerse ni replicarse sin control de autorización/alta inicial segura.
2. **Cookie autenticada:** comprobar CSRF y CORS, `secure`, `httponly`, `samesite`, dominios y path al desplegar detrás de proxy. `HttpOnly` **no** protege frente a CSRF.
3. **Logout/revocación:** no hay endpoint de logout ni revocación global; proponer si procede, no asumir que existe.
4. **`require_secret` por Query:** evita secretos nuevos en URL, preferir header/dependencia segura; URL puede quedar en logs.
5. **Role checks:** el router pacientes exige `admin`; la respuesta de `login` no trae token en JSON, sino cookie. No dar por hecho OAuth2 Bearer.
6. **Esquema:** staging/production requieren Alembic; el ZIP **no** incluye migración universal ni `.env.example`, aunque README menciona este último. Antes de ejecutar, confirmar el fichero de configuración disponible.
7. **Persistencia:** SQLite puede producir datetimes naive; normalizar UTC con cuidado y documentar suposiciones. Un upsert en ORM con reintento no garantiza semántica serializable bajo cualquier aislamiento.
8. **Contrato de respuestas:** en `pacientes`, `PUT` usa `exclude_unset=True`; hay `404` ausente, `409` duplicidad, `503` fallo operativo. Revisar contratos existentes antes de modificar.
9. **Detalles operativos:** logging sin secretos; no hacer limpiezas desde autenticación; `DateTime(onupdate=func.now())` solo cubre actualizaciones emitidas por SQLAlchemy y no writers externos.

## Pruebas disponibles en el ZIP

- `tests/test_models_sqlalchemy.py`: inspección de tablas y ORM SQLite.
- `tests/test_auth_and_cleanup_async.py`: permisos, expiración y limpieza en transacciones async, usando `aiosqlite`.
- `tests/test_authorization_sync_adapter.py`: adaptador de test sync, **no** implementación para producción.
- `tests/conftest.py`: variables de entorno de prueba aisladas.
- El README indica `pytest -q tests` con dependencias de `requirements-dev.txt`. No se afirma aquí que pasen en cualquier máquina.
