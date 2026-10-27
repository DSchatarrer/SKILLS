# Application factory, Flask-Smorest y Marshmallow

Ejemplos originales: [`src/main.py`](../examples/backend_async/src/main.py), [`login/router.py`](../examples/backend_async/src/applications/login/router.py), [`login/schemas.py`](../examples/backend_async/src/applications/login/schemas.py).

- `create_app(settings: Settings | None = None, test_config: Mapping[str, Any] | None = None) -> Flask` es **síncrona** para inicializar Flask, CORS, OpenAPI, Blueprints y CLI. Llama `configure_database(app)` una vez por app. No crea tablas ni limpia sesiones en peticiones.
- Rutas `async def` viven en clases `MethodView` de Flask-Smorest; `@blp.arguments`/`@blp.response` validan y serializan con Marshmallow. `Settings` usa Pydantic Settings; no sustituir schemas de API por Pydantic sin pedirlo.
- `@require_db_session` envuelve `@require_auth` y después `@require_role`; respetar orden. Un decorador sobre `async def` debe esperar al view; las extensiones antiguas pueden requerir `current_app.ensure_sync` y comprobación de compatibilidad.
- Los controllers reciben `AsyncSession` y ejecutan I/O con `await`. Separar HTTP/cookies en router, lógica de dominio en controller, validación en schema y ORM en modelos.
- Nuevo dominio: añadir `applications/<dominio>/router.py`, `controller.py`, `schemas.py`; registrar blueprint en `main.py`; tests por códigos de estado, permisos y serialización.

Documentación Flask: https://flask.palletsprojects.com/en/stable/async-await/ .
