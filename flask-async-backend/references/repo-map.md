# Mapa y contratos del backend de referencia

Fuente original: `flask-async-sqlalchemy-proyecto-completo.zip` / `flask-async-main/backend_async/`. Código byte a byte en [`../examples/README.md`](../examples/README.md). No atribuir esta estructura a otros repositorios sin inspeccionarlos.

```text
backend_async/
├── src/
│   ├── main.py                 # create_app, Api, Blueprints y CORS
│   ├── asgi.py                 # WsgiToAsgi(app)
│   ├── applications/
│   │   ├── home/router.py      # GET / y GET /health
│   │   ├── login/{router,controller,schemas}.py
│   │   └── users/{router,controller,schemas}.py
│   ├── core/
│   │   ├── manager_db.py       # AsyncEngine, async_sessionmaker, inyección
│   │   ├── security.py         # JWT/cookies/roles
│   │   ├── settings.py         # asyncpg/aiosqlite, Pydantic Settings
│   │   ├── commands.py         # Click async bridge
│   │   ├── session_cleanup.py
│   │   └── models/{base,users,sessions}.py
│   └── scripts/cleanup_expired_sessions.py
├── migrations/{env.py,versions/20261027_01_baseline.py}
├── tests/{conftest,test_auth,test_database,test_admin_cli}.py
├── validation/test_*_standalone.py
└── README.md, requirements*.txt, alembic.ini, .env.example
```

Contratos: `GET /` y `GET /health` públicos; `POST /login/` devuelve cookie `X-Sync.Ref`; `POST /login/register` requiere auth + rol admin; `GET /users/users` exige cookie JWT + API key (preferir `X-API-Key`, query legado solo por compatibilidad). Tablas `usuarios` y `sesiones`, JWT persistido y limpieza de sesiones únicamente en CLI.

No migrar estos endpoints, nombres de tablas, schemas, permisos, cookies, ni `main.py` por gusto. Revisar archivo original antes de editar: [`main.py`](../examples/backend_async/src/main.py), [`manager_db.py`](../examples/backend_async/src/core/manager_db.py) y los routers del dominio.
