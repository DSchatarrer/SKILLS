# fastapi-backend — Skill universal para Codex y OpenCode

Skill en español para crear, mantener, revisar y probar APIs con **FastAPI + Python + SQLAlchemy asíncrono + Pydantic v2**. Se inspira en el proyecto `backend_async` del ZIP aportado y en la organización multiarchivo de la skill `research-to-code` del ZIP de ejemplo.

## Instalación rápida (Windows, Linux y macOS)

Extrae el ZIP para que exista una carpeta `fastapi-backend/` con `SKILL.md` en la raíz.

**Un proyecto concreto, ambos agentes (recomendado):**

```bash
python fastapi-backend/scripts/install_skill.py --target both --scope project --project-root RUTA_PROYECTO
```

**Para todos tus proyectos, ambos agentes:**

```bash
python fastapi-backend/scripts/install_skill.py --target both --scope user
```

**Solo OpenCode (ruta nativa):**

```bash
python fastapi-backend/scripts/install_skill.py --target opencode --scope project --project-root RUTA_PROYECTO
```

**Solo Codex:**

```bash
python fastapi-backend/scripts/install_skill.py --target codex --scope user
```

**Comprobar destino sin copiar (recomendado antes de instalar):**

```bash
python fastapi-backend/scripts/install_skill.py --target both --scope project --project-root RUTA_PROYECTO --dry-run
```

Si existe una instalación, el script **no** la pisa; `--force` permite reemplazarla explícitamente. El instalador no necesita paquetes externos, no ejecuta el backend y no contacta internet.

## Por qué solo una carpeta para ambos

Codex busca skills de proyecto en `RUTA_PROYECTO/.agents/skills/`. OpenCode **también** descubre esa misma ubicación, por lo que `--target both` realiza una sola instalación compartida. No instales adicionalmente `.opencode/skills/fastapi-backend` si has usado `both`: podrías duplicar la misma skill. Para OpenCode exclusivamente se admite `.opencode/skills/` (proyecto) o `~/.config/opencode/skills/` (usuario). La ubicación global compartida es `~/.agents/skills/` (en Windows: el directorio de usuario bajo `.agents/skills/`).

## Uso

Desde Codex invoca explícitamente `$fastapi-backend` (o permite la activación automática) y describe la tarea. En OpenCode pídele que use la skill `fastapi-backend`; el sistema puede descubrirla mediante la herramienta nativa de skills. Ejemplos:

- «Usa fastapi-backend para crear un endpoint CRUD de tareas con permisos y tests».
- «Usa fastapi-backend para auditar la creación de administradores y el uso de JWT/cookies».
- «Usa fastapi-backend para convertir una función bloqueante a un flujo async sin compartir AsyncSession».
- «Usa fastapi-backend para diseñar una migración de columnas con Alembic, sin aplicarla».

Si no aparece en el selector, revisa ruta y nombre de carpeta, reinicia el agente y verifica permisos/herramienta skills. La skill **ya incluye una copia literal del backend del ZIP** dentro de `examples/backend_async/`. El agente debe trabajar sobre el repositorio que abras en Codex/OpenCode y consultar esos archivos solo como referencia; no ejecutarlos automáticamente.

## Ejemplos originales del código FastAPI incluidos

La carpeta [`examples/backend_async/`](examples/README.md) contiene **36 archivos** del último ZIP FastAPI disponible, `fastapi-main.zip`, exactamente como los proporcionaste. Además se conserva el `README.md` original de la raíz del ZIP en `examples/source-root-README.md`. El índice por tareas está en `examples/README.md` y `examples/source-manifest.json` contiene los hashes SHA-256 de cada archivo.

Consulta primero los ejemplos específicos cuando quieras crear o mantener partes del backend: `src/main.py`, `src/core/manager_db_async.py`, `src/applications/pacientes/{router,controller,schemas,models}.py`, `src/applications/login/`, `src/core/security.py`, scripts y tests. Se mantiene **todo el código fuente sin reescribir ni corregirlo**; la skill indica qué riesgos no reproducir (como `POST /login/alta-usuario` sin control de acceso).

**Aviso de licencia importante:** `examples/backend_async/LICENSE.md` indica copyright de Iberdrola S.A. y restricción de copia/distribución. Antes de distribuir esta skill con ese contenido a compañeros, repositorios públicos o terceros, asegúrate de tener permiso expreso. La copia incluida no transforma ese código en open source.

```text
fastapi-backend/
├── SKILL.md
├── README.md
├── examples/
│   ├── README.md                 # Mapa de ejemplos según la tarea
│   ├── source-manifest.json      # Hashes SHA-256 originales
│   ├── source-root-README.md     # README del ZIP original, sin modificar
│   └── backend_async/            # Copia literal de 36 archivos originales
│       ├── LICENSE.md
│       ├── requirements*.txt
│       ├── src/                  # main.py, applications/, core/, scripts/
│       └── tests/
├── references/
├── scripts/
├── tests/
└── evals/
```

## Auditoría de solo lectura

Desde la carpeta extraída:

```bash
python fastapi-backend/scripts/audit_backend.py --root RUTA_PROYECTO --format text
python fastapi-backend/scripts/audit_backend.py --root RUTA_PROYECTO --format json
```

Analiza Python mediante AST (sin importar ni ejecutar tu aplicación). Devuelve un inventario aproximado de rutas y avisos para revisión **manual**; no reemplaza análisis dinámico de seguridad.

## Tests de la skill

```bash
python -m unittest discover -s fastapi-backend/tests -v
```

Son pruebas estructurales del empaquetado, del instalador y del analizador; **no** equivalen a probar la ejecución real en Codex/OpenCode. Los escenarios para pruebas manuales se encuentran en `evals/evals.json`.

## Archivos

```text
fastapi-backend/
├── SKILL.md                     # Activación, workflow y reglas principales
├── README.md                    # Instalación, uso y validación
├── references/
│   ├── repo-map.md              # Arquitectura real del backend aportado
│   ├── api-patterns.md          # Routers, schemas, services, contratos
│   ├── database.md              # SQLAlchemy 2 asíncrono
│   ├── security.md              # JWT/cookies/roles/CSRF/CORS
│   └── testing-deploy.md        # Tests, migraciones, despliegue
├── scripts/
│   ├── install_skill.py         # Instalación portable
│   └── audit_backend.py         # Inventario de rutas de solo lectura
├── tests/
│   └── test_skill.py            # Tests offline
└── evals/
    └── evals.json              # Escenarios de evaluación real en agentes
```

## Alcance y procedencia

El ZIP analizado incluía código propietario con restricciones de distribución. Este paquete **no incorpora su código fuente**: describe su arquitectura, contratos y riesgos, y usa ejemplos escritos de nuevo. Destaca la ruta de alta de usuarios sin autorización, que no debe copiarse a aplicaciones públicas.

Recomendaciones de diseño de skills verificadas en guías oficiales de Anthropic (Claude), OpenAI (Codex), OpenCode y la especificación Agent Skills. Referencias: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices ; https://learn.chatgpt.com/docs/build-skills ; https://opencode.ai/docs/skills ; https://agentskills.io/specification .
