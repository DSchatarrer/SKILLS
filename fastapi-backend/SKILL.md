---
name: fastapi-backend
description: Diseñar, crear, mantener, depurar, probar y revisar backends y APIs REST con FastAPI, Python, Pydantic v2 y SQLAlchemy 2 asíncrono. Úsala al crear endpoints, routers, schemas, servicios, modelos ORM, sesiones de base de datos, autenticación JWT/cookies, autorización por roles, migraciones Alembic o tests pytest; especialmente al trabajar con el backend_async de referencia. No usar para tareas solo de frontend ni asumir que cualquier proyecto usa la misma arquitectura.
---

# FastAPI backend — guía operativa para Codex y OpenCode

Construye cambios pequeños, seguros y verificables. Adapta la propuesta a **las dependencias, patrones y contratos del repositorio abierto**; el backend `backend_async/` analizado es una referencia, no una plantilla obligatoria ni un patrón completamente seguro.

## Flujo obligatorio

1. **Inspeccionar antes de escribir.** Localiza `pyproject.toml`/`requirements*.txt`, `src/main.py`, estructura de paquetes, rutas y schemas existentes, gestor de DB, tests y migraciones. Identifica versiones reales, motor SQL, `root_path`, middleware, permisos y convenciones de importación. Si es el backend aportado, lee [references/repo-map.md](references/repo-map.md). No supongas que el ZIP original estará presente en otros proyectos.
2. **Fijar el contrato.** Determina método/ruta, modelo de entrada y salida, estados 2xx/4xx/5xx, permisos, reglas de negocio, idempotencia y compatibilidad de consumidores. En cambios sobre código existente **preserva** rutas, nombres de tablas/columnas, cookies y respuestas salvo que el usuario autorice una ruptura; señala riesgos que impidan una conservación segura.
3. **Elegir capas.** Router HTTP para validación/DI/`response_model`; schemas Pydantic para contratos; servicio para reglas de negocio y transacciones; ORM para persistencia; `core` para dependencias compartidas. Evita servicios monolíticos, routers con SQL y accesos globales a sesiones. Lee [references/api-patterns.md](references/api-patterns.md).
4. **Trabajar correctamente en async.** Un `AsyncEngine` y un `async_sessionmaker` reutilizables por proceso; una **nueva `AsyncSession` por unidad de trabajo/petición**. `await` en operaciones I/O, sin compartir una sesión entre tareas concurrentes. Decide quién hace `commit`/`rollback` y mantenlo consistente; no hagas commits ocultos en dependencias de lectura. Lee [references/database.md](references/database.md).
5. **Definir seguridad antes de exponer rutas.** Autentica y autoriza las operaciones sensibles (incluida creación de usuarios y roles); valida JWT y sesiones revocables si el proyecto usa allowlist; revisa `HttpOnly`, `Secure`, `SameSite`, CSRF, CORS y secretos. Mantén autenticación/lectura **sin efectos secundarios**; limpiezas en jobs separados. Consulta [references/security.md](references/security.md). Nunca repliques una vulnerabilidad conocida como patrón recomendado.
6. **Implementar en incrementos** con modificaciones mínimas; usar SQLAlchemy 2 (`select`, `Mapped`, `mapped_column`), Pydantic v2 (`model_validate`, `model_dump(exclude_unset=True)`) donde correspondan. Evita I/O bloqueante dentro de `async def`; para código síncrono usa `def` cuando FastAPI pueda gestionarlo en threadpool o un adaptador explícito y justificado.
7. **Probar** caso correcto, invalidación, no encontrado, duplicidad, permisos 401/403, expiración, rollback, concurrencia relevante y regresiones. Emplea pytest/pytest-asyncio, HTTPX ASGI transport o TestClient según ciclo de vida y versión, overrides de dependencias y SQLite async solo donde su comportamiento sea representativo; para diferencias críticas usa el DB real. Lee [references/testing-deploy.md](references/testing-deploy.md).
8. **Verificar antes de entregar.** Ejecuta linters, compilación, tests pertinentes y revisión de diff cuando el entorno lo permita; declara lo que **no** se pudo ejecutar. No ejecutes migraciones destructivas, limpiezas, llamadas externas, ni cambies secretos sin autorización. Reporta archivos modificados, contrato, tests exactos y riesgos residuales.

## Reglas de decisión

- **Proyecto existente:** respetar su estructura antes que imponer la estructura de `backend_async`. En refactors, aislar corrección de fallos de cambios de contrato.
- **Proyecto nuevo:** preferir factoría de aplicación/lifespan, configuración tipada por entorno, router por dominio, servicio, schema, modelo y tests; consultar los ejemplos originales de [references/api-patterns.md](references/api-patterns.md).
- **DB:** no usar `create_all()` para migrar staging/producción; generar/revisar migraciones Alembic, backups y plan de reversión. Respetar integridad/índices y las diferencias SQLite/PostgreSQL.
- **HTTP:** `response_model` tipado en endpoints con respuesta de datos, códigos de estado correctos, errores sin detalles internos, paginación para listados potencialmente grandes, y datos sensibles excluidos de respuestas/logs.
- **Riesgo de seguridad:** el ZIP de referencia contiene `/login/alta-usuario` sin autorización y acepta el rol solicitado. No tratarlo como plantilla: exigir autorización/alta controlada. No colocar API keys en parámetros de URL nuevos.
- **Incertidumbre:** nunca inventar ficheros, columnas, tests, versiones, ejecuciones o resultados. Si falta el backend original, aplicar las recomendaciones genéricas y señalar que la comparación es aproximada.

## Guías disponibles (abrir solo al necesitarlas)

| Tarea | Referencia |
| --- | --- |
| Ubicaciones reales, contratos y riesgos del ZIP aportado | [repo-map.md](references/repo-map.md) |
| Añadir CRUD, routers, schemas, servicios, errores HTTP | [api-patterns.md](references/api-patterns.md) |
| SQLAlchemy async, transacciones, upsert, concurrencia | [database.md](references/database.md) |
| JWT, cookies, roles, CSRF, CORS, creación de usuarios | [security.md](references/security.md) |
| Tests, Alembic, CI, observabilidad, entrega | [testing-deploy.md](references/testing-deploy.md) |

## Herramienta opcional

`scripts/audit_backend.py --root /ruta/al/backend_async --format text` realiza **solo lectura**: inventario estático de endpoints y avisos indicativos. No sustituye una auditoría de seguridad ni ejecuta la app. `scripts/install_skill.py` instala esta skill para Codex/OpenCode; sus rutas se explican en `README.md`.

## Formato de entrega de cada cambio

- **Hecho:** módulos, rutas/contratos y garantías mantenidas.
- **Verificado:** comandos ejecutados, resultados reales y tests nuevos/modificados.
- **Pendiente/riesgos:** incompatibilidades, migraciones/manualidades, cobertura no probada.
