# SQLAlchemy 2 asíncrono, sesiones, transacciones

## Sesión por petición/unidad de trabajo

- Crear `AsyncEngine`/`async_sessionmaker` una vez por proceso y cerrarlos durante `lifespan` o teardown.
- Usar una sesión diferente por petición/tarea; `AsyncSession` **no es segura para compartir entre tareas concurrentes**. `asyncio.gather` necesita sesiones independientes.
- Dependencia con `async with factory() as session: yield session`. Para tests, reemplazar dependencia por conexión/sesión aislada.
- Evitar I/O implícito (lazy loading al serializar respuestas); usar estrategias explícitas de carga, `selectinload`, `refresh` y/o DTOs según caso.
- Mantener un propietario de transacción claro. Elegir para cada cambio: servicio hace `commit` + `rollback`, o capa de unidad de trabajo posee `async with session.begin()`; **no mezclar** commits internos si la capa superior necesita atomicidad.

## Consultas y mutations

- SQLAlchemy 2: `select(Model).where(...)`, `session.scalar(...)`, `session.execute(...)`, `session.get(Model, id)`.
- Tras `add`, `await session.flush()` cuando se necesita PK sin confirmar; `commit` al completar la unidad atómica; `refresh` solo cuando procede.
- Capturar `IntegrityError`, ejecutar `await session.rollback()` si la transacción se invalidó, reportar 409 cuando sea violación de unicidad esperada. Evitar convertir todas las `IntegrityError` en duplicidad si hay FK/NOT NULL.
- Evitar consultas N+1; medir y paginar endpoints con tablas grandes. No interpolar entradas de usuario en SQL crudo.
- Para actualizaciones parciales, `payload.model_dump(exclude_unset=True)` y **validar qué atributos pueden modificarse**. Evitar `setattr` sobre claves no autorizadas; no confundir absent con `null`.

## Races e idempotencia

- La secuencia consultar→insertar puede fallar por carrera. Las restricciones únicas **en BD** son necesarias; luego tratar la colisión de forma idempotente o específica.
- El snapshot de `LogsService` hace hasta dos intentos tras `IntegrityError`; no representa un upsert atómico universal. Considera `ON CONFLICT` específico de dialecto si se conoce el motor, o transacciones y locks revisados; añadir prueba simultánea real.
- No prometer portabilidad sin probar SQL generado y aislamiento en PostgreSQL/SQLite/MySQL si el contrato lo requiere.

## Migraciones y tiempo

- `Base.metadata.create_all` solo para pruebas locales o bootstrap temporal, nunca sustituto de Alembic sobre DB existente.
- Verificar autogeneración antes de ejecutar: constraints, índices, nombres, renames, tipos y valores existentes; plan de backup/reversión.
- Usar UTC internamente, datetimes aware en código de dominio, y revisar tipos reales de la DB. SQLite puede devolver naive; documentar suposiciones al normalizar, sin asumir ciegamente que todo naive es UTC.
- `onupdate=func.now()` de SQLAlchemy solo funciona para DML emitido por este ORM, no como trigger SQL universal.

Documentación: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
