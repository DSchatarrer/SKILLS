# backend_async

## Arranque

Instalar `pip install -r requirements.txt`, crear `.env` a partir de `.env.example`
y configurar valores reales. Desde la carpeta `backend`:

```bash
uvicorn main:app --app-dir src --reload
```

El modo `ENVIRONMENT=local` conserva la creación de tablas de desarrollo; staging y
production **no ejecutan create_all**: despliega las migraciones con Alembic.

Para ejecutar una limpieza manual, desde `backend`:

```bash
PYTHONPATH=src python -m scripts.cleanup_expired_sessions
```

En PowerShell:

```powershell
$env:PYTHONPATH="src"
python -m scripts.cleanup_expired_sessions
```

Programa ese comando con cron (Linux) o Programador de tareas (Windows). **No**
lo ejecutes desde una dependencia FastAPI, middleware ni cada petición.
El CLI crea su propia sesión y commit. Comprueba hora UTC del servidor y realiza
una copia de seguridad antes de lanzar limpiezas en producción.

## Advertencias de seguridad y compatibilidad

1. La ruta original `POST /login/alta-usuario` permite crear usuarios y elegir un
   rol sin autenticación. **Esto es peligroso, especialmente con `role=admin`.**
   Se ha conservado para no romper el contrato del API, pero **NO EXPONGAS ese
   endpoint públicamente**: protégelo con `Depends(require_roles('admin'))` después
   de preparar un usuario administrador inicial mediante un procedimiento seguro.
2. No hay logout ni revocación de todas las sesiones para un usuario. Una mejora
   posterior sería añadirlas y registrar intentos de acceso.
3. Las contraseñas y nombres de las variables `.env` se mantienen; no metas
   secretos reales en commits ni logs. Revisa la política CORS existente.
4. Los campos `DateTime(timezone=True)` y formatos de DB pueden cambiar de
   comportamiento entre PostgreSQL y SQLite; SQLite devuelve a menudo horas naive,
   y por eso la autorización normaliza valores persistidos que se asumen UTC.
5. La conversión `created_modificacion`: `server_onupdate=func.now()` del modelo
   original se cambia por `onupdate=func.now()` (funciona en UPDATE de SQLAlchemy,
   pero no en UPDATE externos al ORM). Si necesitas cambios a nivel de DB, usa
   triggers/migraciones propias del motor.
6. La copia de `settings.SQLALCHEMY_DATABASE_URI_ASYNC` es la única usada. Si
   quedan procesos externos que importaban `manager_db_sync`, adáptalos antes de
   desplegar. Se cambian las respuestas `409`/`401` en casos de error.
7. No se incluye una migración universal de esquema: utiliza Alembic `--autogenerate`
   y revisa el SQL antes de aplicarlo a un entorno con datos.
8. Comprobar URLs reales, protección contra CSRF y seguridad de cookies es
   imprescindible antes de producción.

## Pruebas

```bash
pip install -r requirements-dev.txt
pytest -q tests
```

Las pruebas async SQLite requieren `aiosqlite`; se omiten si no está instalado.
El ZIP incluye un parche legible `backend_async.patch` para revisar cada cambio.
