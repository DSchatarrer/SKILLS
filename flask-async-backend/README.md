# flask-async-backend — Skill para Codex y OpenCode

Skill para mantener **Flask asíncrono + SQLAlchemy 2 AsyncSession**, construida a partir de tu último `flask-async-sqlalchemy-proyecto-completo.zip`. Incluye los **46 archivos originales** del ZIP, 6 referencias especializadas, un índice por tareas, un auditor estático, instalador offline, verificador de ejemplos y evaluaciones de activación.

## Instalación en ambos agentes

Descomprime el ZIP de la skill. Abre terminal en la carpeta **que contiene** `flask-async-backend/` y ejecuta:

```powershell
python flask-async-backend/scripts/install_skill.py --target both --scope user
```

Resultado: `~/.agents/skills/flask-async-backend/`, ubicación compartida que **Codex y OpenCode reconocen**. Si ya existe una instalación de esta misma skill y quieres reemplazarla, añade `--force`. No modifica `flask-backend` (síncrona) ni `fastapi-backend`.

Para limitarla a un repositorio:

```powershell
python flask-async-backend/scripts/install_skill.py --target both --scope project --project-root C:\ruta\de\tu\proyecto
```

Instalación solo OpenCode en ruta nativa: `--target opencode`. Codex solo: `--target codex`. Para ver destinos sin escribir: `--dry-run`.

**Activación:** En Codex escribe `$flask-async-backend` o consulta `/skills`; en OpenCode carga `flask-async-backend` mediante su herramienta `skill` o realiza una petición acorde con la descripción. En caso de no aparecer, reinicia la sesión.

## Estructura del ZIP

```text
flask-async-backend/
├── SKILL.md
├── README.md
├── examples/
│   ├── README.md
│   ├── source-manifest.json
│   ├── project-root-README.md
│   └── backend_async/                   # 45 archivos originales completos
│       ├── src/{main.py,asgi.py,applications/,core/,scripts/}
│       ├── migrations/
│       ├── tests/
│       ├── validation/
│       └── requirements.txt, README.md, etc.
├── references/                        # 6 guías temáticas
├── scripts/{install_skill,audit_flask,verify_examples}.py
├── tests/test_skill.py
└── evals/evals.json
```

Los originales se copiaron sin modificarlos. Los únicos archivos adicionales son instrucciones, índices, herramientas y evaluaciones para los agentes.

## Verificar y evaluar

```powershell
python flask-async-backend/scripts/verify_examples.py
python flask-async-backend/scripts/verify_examples.py --source-zip flask-async-sqlalchemy-proyecto-completo.zip
python -m unittest discover -s flask-async-backend/tests -p 'test_*.py' -v
python flask-async-backend/scripts/audit_flask.py --root flask-async-backend/examples/backend_async --format text
```

La verificación de la skill **no ejecuta** endpoints, no instala dependencias ni accede a bases de datos. Los tests HTTP del proyecto de referencia requieren un entorno Flask con `requirements-dev.txt` y una BD local configurada. El ZIP de origen no traía validación completa de integración HTTP ejecutada, así que las pruebas estáticas no demuestran funcionamiento en producción.

## Decisiones de arquitectura respetadas

- Mantiene `create_app()` Flask + Flask-Smorest + Marshmallow y división `router/controller/schemas`.
- Un `AsyncEngine` y un `async_sessionmaker` por app; un `AsyncSession` por operación, `rollback()` explícito y commit desde controller o CLI.
- `NullPool` para evitar conexiones entre event loops WSGI/CLI; drivers `asyncpg` y `aiosqlite`.
- `@asynccontextmanager` con `AsyncGenerator[AsyncSession, None]`, decoradores/auth asíncronos, JWT + cookie `X-Sync.Ref`.
- Comandos Click con `asyncio.run()` **solo en frontera CLI**, Alembic async, limpieza de sesiones fuera de HTTP.
- Adaptador ASGI `WsgiToAsgi` + Hypercorn. **Flask continúa WSGI internamente**.

Nota: los ejemplos reproducen también limitaciones originales (API key en query para clientes heredados y medidas CSRF no implementadas). La skill advierte de ello para que Codex/OpenCode no los repliquen al desarrollar rutas nuevas.

## Referencias oficiales

- [Agent Skills en Codex](https://learn.chatgpt.com/docs/build-skills)
- [Skills en OpenCode](https://opencode.ai/docs/skills)
- [Buenas prácticas de Anthropic](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [Flask async](https://flask.palletsprojects.com/en/stable/async-await/)
- [Flask ASGI](https://flask.palletsprojects.com/en/stable/deploying/asgi/)
- [SQLAlchemy asyncio](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
