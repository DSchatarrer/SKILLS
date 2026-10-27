# Ejemplos originales del último backend Flask asíncrono

Fuente: `flask-async-sqlalchemy-proyecto-completo.zip`, directorio original `flask-async-main/backend_async/`.

Se han incorporado **45 archivos del backend** en `examples/backend_async/` y el README de la raíz original como `examples/project-root-README.md`: **46 archivos copiados literalmente, sin alterar ni reescribir contenido**. El manifiesto [`source-manifest.json`](source-manifest.json) conserva rutas originales, tamaño y SHA-256 de cada archivo. Los nuevos README/índices de la skill no forman parte de esos 46.

## Selección según tarea

| Necesito | Abrir archivos REALES |
| --- | --- |
| Mapa, dependencias y lanzamiento | [README del backend](backend_async/README.md), [requirements.txt](backend_async/requirements.txt), [README raíz](project-root-README.md) |
| Factoría de aplicación, CORS, OpenAPI | [src/main.py](backend_async/src/main.py) |
| Adapter ASGI/Hypercorn | [src/asgi.py](backend_async/src/asgi.py) |
| Motor y sesiones asíncronas | [src/core/manager_db.py](backend_async/src/core/manager_db.py) |
| Drivers, secretos y entorno | [src/core/settings.py](backend_async/src/core/settings.py), [.env.example](backend_async/.env.example) |
| Definir endpoints con Flask-Smorest | [login/router.py](backend_async/src/applications/login/router.py), [users/router.py](backend_async/src/applications/users/router.py), [home/router.py](backend_async/src/applications/home/router.py) |
| Controladores y negocio await | [login/controller.py](backend_async/src/applications/login/controller.py), [users/controller.py](backend_async/src/applications/users/controller.py) |
| Validación API Marshmallow | [login/schemas.py](backend_async/src/applications/login/schemas.py), [users/schemas.py](backend_async/src/applications/users/schemas.py) |
| JWT, cookie, autorización, API key | [core/security.py](backend_async/src/core/security.py) |
| Modelos SQLAlchemy | [models/users.py](backend_async/src/core/models/users.py), [models/sessions.py](backend_async/src/core/models/sessions.py), [models/base.py](backend_async/src/core/models/base.py) |
| Comandos Click con asyncio | [core/commands.py](backend_async/src/core/commands.py) |
| Limpieza de sesiones fuera de HTTP | [core/session_cleanup.py](backend_async/src/core/session_cleanup.py), [scripts/cleanup_expired_sessions.py](backend_async/src/scripts/cleanup_expired_sessions.py) |
| Alembic async, migraciones | [migrations/env.py](backend_async/migrations/env.py), [baseline](backend_async/migrations/versions/20261027_01_baseline.py), [guía de migraciones](backend_async/migrations/README.md) |
| Fixtures/pruebas integradas | [tests/conftest.py](backend_async/tests/conftest.py), [tests/test_auth.py](backend_async/tests/test_auth.py), [tests/test_database.py](backend_async/tests/test_database.py), [tests/test_admin_cli.py](backend_async/tests/test_admin_cli.py) |
| Comprobaciones offline del proyecto | [validation/test_architecture_standalone.py](backend_async/validation/test_architecture_standalone.py), [validation/test_async_settings_standalone.py](backend_async/validation/test_async_settings_standalone.py), [validation/test_sqlalchemy_standalone.py](backend_async/validation/test_sqlalchemy_standalone.py) |
| Reporte de conversión previo | [CONVERSION_REPORT.json](backend_async/CONVERSION_REPORT.json) |

## Precauciones

- **No modifiques los ejemplos** para trabajar en el proyecto de destino: utilízalos como referencia y cambia solo los archivos del repositorio del usuario.
- El código de referencia permite un `apikey` de URL por compatibilidad y usa cookies sin medidas CSRF específicas: **no replicar como recomendación para rutas nuevas**.
- Flask ejecuta vistas async sobre su capa WSGI; `WsgiToAsgi` no convierte la aplicación en ASGI nativo.
- El ZIP se generó sin pruebas de integración HTTP ejecutadas en ese momento por falta de dependencias. La presencia de tests no garantiza que pasen en todos los entornos.
- `src/main.py` contiene configuración de desarrollo; no utilizar secretos de `.env.example` en producción.

## Validar integridad de ejemplos

Desde la raíz de la skill:

```sh
python scripts/verify_examples.py
```

Este script verifica que los archivos locales mantienen el SHA-256 copiado del ZIP original. Para probar el código HTTP/DB, instala las dependencias y ejecuta sus propios tests desde `examples/backend_async/` o, preferentemente, sobre el proyecto real.
