# flask-backend — Skill para Codex y OpenCode

Skill en español para **mantener y desarrollar backends Flask síncronos** con arquitectura modular, Flask-Smorest, Marshmallow, SQLAlchemy 2, JWT/cookies, autorización y Alembic. Su referencia arquitectónica es **la última versión elegida**: `flask-estructura-fastapi-tipado-corregido.zip` (`flask-main/backend_sync/`). La estructura de la skill sigue el patrón `SKILL.md` + `examples/` + `references/` + `scripts/` + `tests/` + `evals/` del ZIP original `SKILLS-main.zip`.

**No modifica el proyecto Flask al instalarse**: solo añade las instrucciones de agente. No contiene credenciales ni ficheros `.env` reales. **Sí contiene una copia literal del backend original en `examples/backend_sync/`** (incluido únicamente `.env.example`, con marcadores de sustitución), para que el agente use tu implementación como referencia. La skill no convierte Flask en FastAPI y **no sustituye tu `manager_db.py`**.

## Instalación en Windows / Linux / macOS

Extrae el ZIP; verás `flask-backend/` con `SKILL.md` directamente dentro. Ejecuta desde la carpeta que contiene `flask-backend/`:

```bash
# Instalación compartida en UN proyecto (recomendado)
python flask-backend/scripts/install_skill.py --target both --scope project --project-root RUTA_PROYECTO

# Instalar para TODOS los proyectos del usuario, compartida por ambos agentes
python flask-backend/scripts/install_skill.py --target both --scope user

# Mostrar qué se haría, sin instalar
python flask-backend/scripts/install_skill.py --target both --scope project --project-root RUTA_PROYECTO --dry-run
```

El instalador estándar Python no necesita paquetes adicionales. **`both` instala una sola copia** en `RUTA_PROYECTO/.agents/skills/flask-backend/` (o `~/.agents/skills/flask-backend/` en ámbito user), porque **Codex y OpenCode leen esa ruta**. Evita copiarla además en `.opencode/skills/` con el mismo nombre: OpenCode podría seleccionar una definición distinta por precedencia.

Opciones para uno solo:

```bash
python flask-backend/scripts/install_skill.py --target codex --scope user
python flask-backend/scripts/install_skill.py --target opencode --scope project --project-root RUTA_PROYECTO
```

Para OpenCode en solitario, la ubicación nativa es `.opencode/skills/flask-backend/` en proyecto o `~/.config/opencode/skills/flask-backend/` global. Puedes copiar la carpeta manualmente a esas ubicaciones. **No** se sobrescribe instalación previa sin `--force`; este flag reemplaza el contenido de esa skill y debe usarse solo si lo deseas.

### Ejemplo con PowerShell (Windows)

```powershell
python .\flask-backend\scripts\install_skill.py --target both --scope project --project-root "C:\ruta\mi-flask"
```

## Uso

Con Codex invoca `$flask-backend` o permite detección automática. Con OpenCode pide `usa la skill flask-backend` o actívala mediante su herramienta de skills; las interfaces de invocación pueden variar por versión.

Ejemplos de tareas:

- «Usa flask-backend para crear un módulo `products` conservando la estructura applications/core y añadiendo tests».
- «Revisa `manager_db.py` sin cambiar mi ciclo de Session ni el `rollback` explícito».
- «Añade una ruta protegida con Flask-Smorest, Marshmallow, auth JWT y permisos y verifica los decoradores».
- «Corrige un 401/403 en `POST /login/register` respetando contratos y crea tests».
- «Revisa una migración Alembic de `usuarios` sin aplicarla sobre datos reales».
- «Mantén la API key por header en un endpoint nuevo sin replicar `?apikey=`».

## Ejemplos extraídos de tu ZIP (sin recrear el código)

La carpeta [`examples/backend_sync/`](examples/backend_sync/) contiene **todos los archivos originales** de `flask-estructura-fastapi-tipado-corregido.zip` bajo `flask-main/backend_sync/`, intactos. Por ejemplo:

- [`src/main.py`](examples/backend_sync/src/main.py) — application factory y Blueprints.
- [`src/core/manager_db.py`](examples/backend_sync/src/core/manager_db.py) — tu `sessionmaker` con `class_=Session` y `Generator[Session, None, None]`.
- [`src/applications/login/router.py`](examples/backend_sync/src/applications/login/router.py) — endpoints y decoradores reales.
- [`src/applications/login/controller.py`](examples/backend_sync/src/applications/login/controller.py) — negocio y commits.
- [`src/core/security.py`](examples/backend_sync/src/core/security.py) — JWT, roles y cookie.
- [`tests/test_auth.py`](examples/backend_sync/tests/test_auth.py) — tests originales.
- [`migrations/versions/20261027_01_baseline.py`](examples/backend_sync/migrations/versions/20261027_01_baseline.py) — migración original.

Lee el [índice de ejemplos](examples/README.md) para acceder a todos los módulos. El [`source-manifest.json`](examples/source-manifest.json) incorpora SHA-256 por archivo para verificar que la copia es idéntica al ZIP original. Estos ejemplos **no se ejecutan automáticamente** ni modifican el proyecto donde instalas la skill.

## Auditoría estática, sin arrancar la app

```bash
python flask-backend/scripts/audit_flask.py --root RUTA_PROYECTO/backend_sync --format text
python flask-backend/scripts/audit_flask.py --root RUTA_PROYECTO/backend_sync --format json
```

Lee fuentes `.py` con AST, descubre rutas literales `flask_smorest.Blueprint` + `MethodView`, algunas `@blp.get`/`@app.route`, y señala patrones que revisar: decoradores de auth, register público aparente, `@contextmanager -> Iterator`, DB factory dentro de `applications`, API key heredada en query. **No importa archivos ni ejecuta endpoints**. Sus hallazgos pueden omitir comportamientos dinámicos o arrojar falsos positivos.

## Test de empaquetado e instalador

```bash
python -m unittest discover -s flask-backend/tests -v
```

Estos tests comprueban la estructura de la skill, ubicaciones, dry-run, instalación, overwrite explícito, rechazo de enlaces simbólicos, heurísticas del auditor y la integridad de todos los ejemplos copiados del último ZIP. Se entregan también escenarios para evaluación manual en `evals/evals.json`. **No equivale a haber evaluado la skill en sesiones reales de Codex y OpenCode**, ni a ejecutar tests del backend original.

## Contenido

```text
flask-backend/
├── SKILL.md
├── README.md
├── examples/
│   ├── README.md                 # Índice de ejemplos de código REAL
│   ├── source-manifest.json      # SHA-256 y proveniencia de cada archivo
│   └── backend_sync/             # Copia íntegra del backend del último ZIP
│       ├── src/                 # main, applications, core, scripts
│       ├── migrations/          # Alembic real
│       ├── tests/               # Tests reales
│       ├── validation/          # Validaciones originales
│       └── ...                  # requirements, README, .env.example
├── references/
│   ├── repo-map.md
│   ├── app-factory-routing.md
│   ├── database-di.md
│   ├── auth-security.md
│   └── testing-migrations.md
├── scripts/
│   ├── install_skill.py
│   └── audit_flask.py
├── tests/
│   └── test_skill.py
└── evals/
    └── evals.json
```

## Fuentes contrastadas

- Claude/Anthropic, buenas prácticas de skills (descripción, frontmatter, instrucciones compactas, carga progresiva): https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
- Codex/OpenAI, formato, invocación y rutas: https://learn.chatgpt.com/docs/build-skills
- OpenCode, rutas compartidas, búsqueda e invocación: https://docs.opencode.ai/docs/skills/
- Flask, factoría y contexto: https://flask.palletsprojects.com/en/stable/patterns/appfactories/ ; https://flask.palletsprojects.com/en/stable/appcontext/
- Flask-Smorest, Blueprints, MethodView y Marshmallow: https://flask-smorest.readthedocs.io/en/latest/quickstart.html
- SQLAlchemy 2, ciclo de Session y sessionmaker: https://docs.sqlalchemy.org/en/20/orm/session_basics.html
- OWASP CSRF: https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html

Estas fuentes sirven para mantener la skill al día; al hacer cambios de API sensibles a versiones, verificar documentación de las versiones instaladas en el proyecto concreto.
