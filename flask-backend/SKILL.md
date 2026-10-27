---
name: flask-backend
description: Crear, mantener, auditar, refactorizar y probar backends Flask síncronos con arquitectura src/applications/core, application factory create_app, Flask-Smorest, Marshmallow, SQLAlchemy 2, inyección de Session, JWT/cookies, roles y Alembic. Aplicar en APIs Flask existentes o nuevas; especialmente proyectos con backend_sync. No usar para FastAPI ni cambios exclusivamente frontend.
---

# Flask Backend — skill para Codex y OpenCode

Trabaja como ingeniero de backend Flask. Prioriza **el contrato existente, cambios pequeños, seguridad verificable y pruebas**. Esta skill toma como patrón de arquitectura el ZIP más reciente `flask-estructura-fastapi-tipado-corregido.zip` (`flask-main/backend_sync/`) y, para la forma de la skill, `research-to-code` de `SKILLS-main.zip`. **Incluye una copia literal verificable del backend Flask original** en [`examples/backend_sync/`](examples/README.md), de modo que el agente pueda leer sus ejemplos aunque el ZIP de origen no esté disponible en el proyecto. La skill sirve también en otros repositorios Flask.

## Cuándo activarla

- Diseñar o modificar endpoints Flask, Blueprints Flask-Smorest, controladores, Marshmallow, ORM, autenticación, permisos, pruebas, CLI o migraciones.
- Diagnosticar problemas de sesiones, `sessionmaker`, contextos Flask, decoradores, cookies JWT, CORS, CSRF, o aplicación de Alembic.
- Convertir/refactorizar un backend Flask hacia la **organización** `src/applications/core`, sin convertirlo a FastAPI.
- **No** activarla para APIs FastAPI/Starlette, interfaces React o tareas sin relación con Flask.

## Flujo obligatorio

1. **Inspecciona antes de editar.** Identifica raíz del backend, `create_app`, Blueprints registrados, `requirements`, sesiones/transacciones, schemas, modelos, migraciones y tests. Comprueba rutas y contratos existentes; nunca inventes archivos ni columnas. Para la referencia entregada lee [repo-map.md](references/repo-map.md) y el [índice de ejemplos reales](examples/README.md).
2. **Conserva el diseño acordado.** En el proyecto de referencia usa `flask-main/backend_sync/src/` y respeta `main.py` → `applications/<dominio>/{router,controller,schemas}.py` → `core/{manager_db,security,settings,models}`. Si el proyecto real difiere, **adapta** en vez de imponer cambios ajenos al encargo. Lee [app-factory-routing.md](references/app-factory-routing.md) y, si modificas arquitectura, el código literal de [create_app](examples/backend_sync/src/main.py).
3. **Usa Flask síncrono y dependencias por operación.** Reutiliza un `Engine` y un `sessionmaker` **por instancia de app** (`app.extensions`), crea una `Session` por operación HTTP/CLI, pasa `db` al controlador y no la compartas entre hilos. Mantén `class_=Session`, `expire_on_commit=False`, `pool_pre_ping=True`, `pool_recycle=1800` y `rollback()` explícito **si estás trabajando sobre el backend de referencia**, salvo petición expresa. Usa `@contextmanager` con anotación `Generator[Session, None, None]`. Ningún commit automático en `require_db_session`. Lee [database-di.md](references/database-di.md) y el [manager_db original](examples/backend_sync/src/core/manager_db.py).
4. **Separa contratos y negocio.** Los routers hacen HTTP, validación, cookies y mapeo de errores; los controllers gestionan negocio y escritura; `schemas.py` usa Marshmallow; los modelos son SQLAlchemy 2; `core` centraliza infraestructura compartida. No conviertas a Pydantic las peticiones existentes solo porque `Settings` use Pydantic Settings.
5. **Protege rutas antes de ampliar su exposición.** Si las funciones necesitan `db`, conserva el orden de decoradores para que `@require_db_session` envuelva `@require_auth()` y `@require_role(...)`. Mantén `/login/register` protegido por rol `admin`, cookie `X-Sync.Ref`, verificación de sesión persistida y API key preferiblemente por `X-API-Key`. No copies `?apikey=` a rutas nuevas. Revisa CSRF en escrituras autenticadas mediante cookies y no habilites CORS `*` con credenciales. La autenticación **no elimina sesiones**. Lee [auth-security.md](references/auth-security.md) y los [routers reales de login](examples/backend_sync/src/applications/login/router.py).
6. **Preserva política transaccional y mantenimiento.** Controllers/servicios deciden `commit()` de escrituras; context manager cierra y hace `rollback` al fallar; CLI puede usar `factory.begin()`. Limpieza de sesiones en tarea externa/CLI, jamás en un GET/auth. No crees tablas ni ejecutes migraciones en cada petición. Lee [testing-migrations.md](references/testing-migrations.md) y los [tests reales de autenticación](examples/backend_sync/tests/test_auth.py).
7. **Modifica por incrementos y prueba.** Primero reproduce si arreglas un fallo. Prueba 200/201, 400/401/403/404/409, cookies, expiración, permisos, rollback, que auth no haga DELETE y que las rutas legadas sigan iguales. Emplea `app.test_client()`, `app.test_cli_runner()` y fixtures con SQLite aislado cuando corresponda. Prueba con PostgreSQL si afectan diferencias de dialecto.
8. **Valida y comunica.** Si el entorno lo permite ejecuta `python -m compileall -q src tests migrations`, `pytest -q`, linters configurados y `git diff`. Nunca afirmes que un test pasó si no se ejecutó. Describe archivos, rutas/contratos modificados y riesgos pendientes. No apliques migraciones reales, limpiezas, cambios de secretos, accesos a producción ni operaciones destructivas sin autorización.

## Reglas para respetar el backend de referencia

- **No reescribir** `manager_db.py` por estilo; las simplificaciones (`class_=Session`, doble llamada `get_session_factory()()`, `except BaseException`) son opcionales y **no** son fallos. El único ajuste solicitado previamente fue `Iterator[Session]` → `Generator[Session, None, None]`.
- No introducir Flask-SQLAlchemy, `scoped_session`, `AsyncSession`, una clase `DatabaseManager` o un singleton global para reemplazar el `app.extensions` actual sin necesidad demostrada.
- Mantener la factoría `create_app(settings=None, test_config=None)`, Blueprints de Flask-Smorest, Marshmallow y los nombres de las tablas `usuarios` / `sesiones` y sus columnas existentes.
- Conservar `GET /`, `GET /health`, `POST /login/`, `POST /login/register`, `GET /users/users` y la cookie `X-Sync.Ref` hasta que el usuario solicite un cambio de contrato. Para producción revisar limitación de intentos de login, CSRF, política de roles y seguridad de secretos; no presentar el repo como una solución totalmente endurecida.
- `init_db()` / `Base.metadata.create_all()` son **solo** bootstrap o desarrollo; evolución del esquema con Alembic revisado y migraciones verificadas.

## Ejemplos de código REAL del último ZIP (carga progresiva)

El [índice de `examples/`](examples/README.md) enlaza al backend original completo y orienta sobre qué archivo abrir según la tarea. **Estos ejemplos son archivos del último ZIP copiados sin reescrituras ni simplificaciones**. Cuando programes:

- Base de datos/inyección: consulta [`examples/backend_sync/src/core/manager_db.py`](examples/backend_sync/src/core/manager_db.py).
- Factoría/rutas: consulta [`examples/backend_sync/src/main.py`](examples/backend_sync/src/main.py) y [`examples/backend_sync/src/applications/login/router.py`](examples/backend_sync/src/applications/login/router.py).
- Controllers/contratos: consulta [`examples/backend_sync/src/applications/login/controller.py`](examples/backend_sync/src/applications/login/controller.py) y [`examples/backend_sync/src/applications/login/schemas.py`](examples/backend_sync/src/applications/login/schemas.py).
- Auth: consulta [`examples/backend_sync/src/core/security.py`](examples/backend_sync/src/core/security.py).
- Migraciones/pruebas/CLI: usa el índice para abrir los archivos originales que correspondan.

Usa estos archivos como **patrón fiel**, no como instrucciones de copiar el proyecto entero, y no conviertas comportamientos legados (p. ej. `?apikey=`) en recomendación para endpoints nuevos. La integridad se documenta en [`examples/source-manifest.json`](examples/source-manifest.json).

## Referencias (carga progresiva)

| Tema de la petición | Abrir archivo |
| --- | --- |
| Código real del último ZIP (ejemplos completos) | [examples/README.md](examples/README.md) |
| Rutas reales y estructura del último ZIP | [repo-map.md](references/repo-map.md) |
| Factoría, Blueprints, MethodView, Marshmallow, decorators | [app-factory-routing.md](references/app-factory-routing.md) |
| SQLAlchemy síncrono, `Session`, DI, transacciones y CLI | [database-di.md](references/database-di.md) |
| JWT, sesiones persistidas, cookies, roles, CORS, CSRF | [auth-security.md](references/auth-security.md) |
| pytest, test client, Alembic y despliegue | [testing-migrations.md](references/testing-migrations.md) |

## Herramientas de esta skill

- `python scripts/audit_flask.py --root RUTA_BACKEND --format text`: inventario **estático y de solo lectura** de rutas y señales de revisión; no importa ni arranca la aplicación; no es auditoría de seguridad completa.
- `python scripts/install_skill.py --target both --scope project --project-root RUTA`: instalación única en `.agents/skills/flask-backend`, compartida por Codex y OpenCode. Véase `README.md`.

## Formato de respuesta al usuario

- **Cambios:** archivos y contratos afectados.
- **Validación:** comandos ejecutados y resultados observados; distingue los tests no ejecutados.
- **Precauciones:** seguridad, migraciones y compatibilidad pendientes cuando apliquen.
