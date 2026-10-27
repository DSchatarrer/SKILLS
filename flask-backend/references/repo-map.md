# Mapa fiel de la última versión Flask

Origen: `flask-estructura-fastapi-tipado-corregido.zip`, ruta dentro del archivo `flask-main/backend_sync/`. El backend completo del ZIP **sí se entrega** como copia literal de referencia en [`examples/backend_sync/`](../examples/README.md), con SHA-256 registrado en [`examples/source-manifest.json`](../examples/source-manifest.json). No inventes ficheros en repositorios ajenos.

```text
flask-main/
└── backend_sync/
    ├── src/
    │   ├── main.py
    │   ├── applications/
    │   │   ├── home/{router.py,__init__.py}
    │   │   ├── login/{router.py,controller.py,schemas.py,__init__.py}
    │   │   └── users/{router.py,controller.py,schemas.py,__init__.py}
    │   ├── core/
    │   │   ├── manager_db.py
    │   │   ├── settings.py
    │   │   ├── security.py
    │   │   ├── session_cleanup.py
    │   │   ├── commands.py
    │   │   └── models/{base.py,users.py,sessions.py,__init__.py}
    │   └── scripts/cleanup_expired_sessions.py
    ├── migrations/{env.py,versions/20261027_01_baseline.py,...}
    ├── tests/{conftest.py,test_auth.py,test_database.py,test_admin_cli.py}
    ├── validation/{test_architecture_standalone.py,test_sqlalchemy_standalone.py}
    ├── requirements.txt
    ├── requirements-dev.txt
    ├── alembic.ini
    └── .env.example
```

El nombre `backend_sync` hace explícito Flask con SQLAlchemy **síncrono**; su equivalente estructural previo en FastAPI era `backend_async`, pero **no** se deben mezclar sus APIs ni convertidores.

## Contratos reales

| HTTP/CLI | Comportamiento observado en fuentes |
| --- | --- |
| `GET /` | Home |
| `GET /health` | Health JSON `{"status":"ok"}` |
| `POST /login/` | Login; `LoginRequestSchema`; cookie JWT `X-Sync.Ref`; responde 200 o 401 |
| `POST /login/register` | Alta `RegisterRequestSchema` tras JWT + rol admin; 201, 401, 403, 409 |
| `GET /users/users` | Ruta legado; requiere cookie de autenticación + API key; devuelve `{"hola":"<usuario>"}` |
| `flask ... init-db` | Bootstrap desarrollo; no migración productiva |
| `flask ... create-admin` | Crear primer administrador fuera de HTTP |
| `flask ... cleanup-sessions` | Eliminar sesiones caducadas fuera de peticiones |

**Detalles de datos**: tabla `usuarios` (`usu`, `hash_pwd`, `role`); tabla `sesiones` (`token`, `usu`, `exp`); PK actuales `usuarios.usu` y `sesiones.token`. Para introducir claves externas, constraints o nuevas columnas hay que diseñar migración y tests. JWT contiene `sub` como id de sesión UUID y `exp`; sesión persistida se consulta por `sub` y permite invalidación. La API key se prefiere en cabecera `X-API-Key`; consulta `apikey` está admitida solo como legado.

**Stack del ZIP:** Flask 3.1.x, Flask-Smorest 0.46.x, Flask-CORS, SQLAlchemy 2.x sync, Marshmallow 4.x, Pydantic Settings 2 para configuración, python-jose, Werkzeug, Alembic, pytest. Verifica dependencias/versions de **cada** repositorio antes de usar APIs sensibles a versión.

## Qué no se debe modificar por defecto

- `create_app()` no crea tablas ni limpia sesiones; registra extensiones, API, Blueprints, CLI.
- `manager_db.py` produce Engine + sessionmaker una vez por app; `@require_db_session` por operación, sin commit implícito.
- Auth y role checks consultan DB sin modificar ni borrar registros.
- El `controller.py` de login hace commits explícitos cuando crea sesiones o usuarios.
- Los schemas HTTP son Marshmallow; la configuración env está tipada con `Settings` (Pydantic Settings).
- Las rutas y nombres existentes son un contrato; no renombrar `/users/users` solo por estética.

## Pendientes explícitos en README del backend

Antes de llamar al backend "listo para producción": protección CSRF en mutaciones autenticadas con cookie, rate limiting para login, revisión de quién puede solicitar roles y auditoría de accesos. Marcar como revisión pendiente sin cambiar funcionalidad si el usuario pide únicamente una modificación organizativa.
