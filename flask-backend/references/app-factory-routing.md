# Factoría Flask, Blueprints y organización de endpoints

## Estructura que hay que respetar

- `src/main.py`: `create_app(settings: Settings | None = None, test_config: Mapping[str, Any] | None = None) -> Flask`; configura Flask, CORS opcional, `configure_database(app)`, `Api(app)`, componentes OpenAPI, Blueprints y CLI; devuelve `app`.
- `src/applications/<dominio>/router.py`: `flask_smorest.Blueprint` + `flask.views.MethodView`, decoradores de entrada/salida, auth/cookies, códigos HTTP; no SQL de negocio.
- `src/applications/<dominio>/schemas.py`: `marshmallow.Schema` y fields para `@blp.arguments` / `@blp.response`; no sustituir por clases Pydantic sin un cambio explícito de arquitectura.
- `src/applications/<dominio>/controller.py`: negocio con `Session` inyectada cuando se necesita; errores de dominio hacia router para mapear a `abort()`.
- `src/core/*`: settings, base de datos, seguridad, modelos, mantenimiento, CLI.

## Patrón de endpoint

Ejemplo **nuevo e ilustrativo** de consulta, no es un archivo del ZIP:

```python
from flask.views import MethodView
from flask_smorest import Blueprint
from src.core.manager_db import require_db_session
from src.core.security import require_auth

blp = Blueprint("items", "items", url_prefix="/items", description="Items")

@blp.route("/")
class ItemList(MethodView):
    @blp.response(200, ItemListSchema)
    @require_db_session
    @require_auth()
    def get(self, *, db):
        return ItemController(db).list_items()
```

**No copies el ejemplo sin crear/importar el schema y controller apropiados.** Ajusta rutas/códigos/decisiones al proyecto. En casos con `@blp.arguments`, recuerda que Flask-Smorest inyecta datos deserializados en la vista; si el wrapper no conserva `*args, **kwargs`, romperá la llamada.

## Orden de los decoradores

Para rutas con `@require_auth()` el contrato del código existente exige que `@require_db_session` esté **por fuera** de `@require_auth()`, pues añade `db` a `kwargs` antes de validar JWT y consultar `Sessions`/`Users`. Cuando se usa rol, `@require_role("admin")` va **dentro** de `@require_auth()`. Ejemplo real de orden (decoradores de flask-smorest arriba):

```python
@blp.arguments(RegisterRequestSchema)
@blp.response(201, MessageSchema)
@require_db_session
@require_auth()
@require_role("admin")
def post(self, credentials, *, db):
    ...
```

No alteres el orden por estética; añade tests 401/403/201 para comprobarlo. Las funciones decoradas usan `functools.wraps` para conservar metadatos.

## Configuración y contexto

- `configure_database(app)` recibe el objeto real cuando se crea la aplicación, no usa `current_app` durante inicialización.
- Código de rutas, CLI o tareas con contexto puede acceder a `current_app`. Scripts externos llaman `with app.app_context():` si dependen de `get_session_factory()` o settings de la aplicación.
- No importes `app` globalmente desde Blueprints; evita importaciones circulares.
- No cambies `@app.route` o `@blp.route` sin comprobar si es Blueprint estándar Flask o Flask-Smorest.
- `test_config` debe aplicarse antes de configurar el Engine para no conectar a una BD equivocada durante tests.

## Crecimiento del proyecto

Para un dominio nuevo, añade solo los módulos que realmente requiera. No crear abstracciones sin motivo (`repositories`, `services`, etc.); si el dominio crece, documenta por qué añadir una capa. Mantén rutas versionadas si el contrato lo exige, sin cambiar silenciosamente rutas legadas.

Documentación oficial: https://flask.palletsprojects.com/en/stable/patterns/appfactories/ ; https://flask.palletsprojects.com/en/stable/appcontext/ ; https://flask-smorest.readthedocs.io/en/latest/quickstart.html
