# Flask WSGI y ASGI adaptado

Archivo original: [`src/asgi.py`](../examples/backend_async/src/asgi.py): `asgi_app = WsgiToAsgi(create_app())`.

- **Flask sigue siendo WSGI**: `async def` permite I/O concurrente dentro de una vista, pero una request ocupa un worker y no transforma su concurrencia HTTP en ASGI nativo.
- `asgiref.wsgi.WsgiToAsgi` proporciona interfaz ASGI y mantiene un loop; Hypercorn sirve `src.asgi:asgi_app`. Adaptador **no** es migración a Quart/FastAPI.
- Las tareas `asyncio.create_task` creadas en una vista Flask bajo WSGI tradicional pueden cancelarse cuando concluye; tareas persistentes requieren queue externa o arquitectura específica.
- Extensiones antiguas sin soporte async pueden romper views; validar decoradores y uso de `ensure_sync` de Flask. Flask-Smorest/Marshmallow mantienen sus contratos.
- `NullPool` del ejemplo evita conexiones cruzadas entre loops WSGI, CLI y tests. Solo plantear pooling de larga vida tras revisar despliegue ASGI, ownership del engine y rendimiento.

Desde `backend_async/` (con `.env` y dependencias preparadas):

```sh
python -m pip install -r requirements-dev.txt
flask --app src.main:create_app init-db  # SOLO BD nueva/desarrollo
flask --app src.main:create_app create-admin --username admin
hypercorn src.asgi:asgi_app --bind 127.0.0.1:5000
```

No arrancar `init-db` en cada release. `flask run` es servidor de desarrollo. Para escalado HTTP ASGI nativo, evaluar migración explícita a Quart o FastAPI con validación contractual.

Fuentes: https://flask.palletsprojects.com/en/stable/async-await/ , https://flask.palletsprojects.com/en/stable/deploying/asgi/ , https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html .
