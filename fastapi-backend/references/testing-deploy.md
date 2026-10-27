# Tests, migraciones, despliegue y entrega

## Tests en pirámide

- **Unitarios de servicio:** normalización, reglas de negocio, validación, faltantes, permisos, rollback y manejo de excepciones. Mock selectivo; no afirmar comportamiento de DB a partir de un mock.
- **Integración HTTP:** HTTPX `ASGITransport` con lifespan gestionado cuando sea necesario, o `TestClient` compatible con versión instalada. Usa `app.dependency_overrides[dependencia_real] = fake` y deshaz override en `finally`/fixture de teardown; el objeto clave debe ser el mismo que importó la ruta.
- **DB async:** `pytest-asyncio` y `aiosqlite` sirven para lógica básica, constraints y transacciones; una DB en memoria y distintas conexiones pueden requerir StaticPool/aislamiento apropiado. SQLite no equivale siempre a PostgreSQL: testear en el motor real lo crítico (locks, on conflict, timezones, migraciones, constraints).
- **Seguridad:** contraseña errónea, cookie ausente/inválida/caducada, sesión revocada, roles distintos, autorización por recurso, CSRF, alta admin protegida y no filtración de credenciales.
- **Regresión del snapshot:** mantener `root_path`, rutas, nombres de tabla/columnas, cookie `X-Sync.Ref` y respuestas salvo decisión explícita.

## Matriz mínima según cambio

| Cambio | Pruebas recomendadas |
| --- | --- |
| GET público/privado | 200, 401, 403, 404, filtros, paginación, response_model |
| Crear | 201/200 según contrato, 422, 409, rollback, auth, constraints |
| Actualizar/borrar | éxito, ausente, propiedad del recurso, 409, atomía, idempotencia definida |
| JWT/cookie/sesión | firma y expiración, revocación, roles, no side effects de lectura |
| Migración | upgrade/downgrade ensayados en clon, índices, colisiones y rollback |

## Comandos orientativos para `backend_async/`

Solo si coinciden layout y dependencias reales del checkout; no afirmar tests ejecutados si faltan paquetes.

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q tests
python -m compileall -q src
uvicorn main:app --app-dir src --reload
```

El README de referencia usa `PYTHONPATH=src python -m scripts.cleanup_expired_sessions`, solo para limpiezas programadas. No ejecutarlo como verificación automática. En PowerShell, `PYTHONPATH` se configura con `$env:PYTHONPATH = "src"`.

## Producción

- Entorno explícito (`local`/`staging`/`production`), secretos en variables/secret store, debug desactivado, trusted hosts/proxies configurados.
- Ejecutar migraciones Alembic revisadas manualmente con backup, plan de reversión y permisos mínimos de DB. Nunca `create_all()` automático en staging/production.
- Observabilidad: logs estructurados con request id, métricas y alertas sin secretos ni PHI; health checks de readiness/liveness sin abusar de DB.
- Pool de conexiones y timeouts calculados para workers; graceful shutdown/dispose; evitar tareas periódicas por request o duplicadas en varios workers.

## Presentación de resultados

Informar: (a) contrato/tareas completadas, (b) archivos editados, (c) comandos efectivamente ejecutados y su salida resumida, (d) tests omitidos y razón, (e) riesgos/acciones antes de producción. Tests estructurales de skill ≠ pruebas end-to-end de Codex/OpenCode.

Fuentes: https://fastapi.tiangolo.com/advanced/testing-dependencies/ ; https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/
