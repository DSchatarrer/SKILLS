# Endpoints, validación y organización

## Al ampliar el proyecto de referencia

Coloca funcionalidades de dominio en `src/applications/<dominio>/{router.py,controller.py,schemas.py,models.py}` siguiendo los módulos existentes; reutiliza `core.manager_db_async.get_session`, `core.security.require_roles` cuando aplique, `core.models.base.Base`, logger y el `include_router` en `create_app`. No edites modelos o URLs existentes para adaptar un ejemplo genérico. Para apps nuevas el nombre de paquete puede cambiar.

## Contrato primero

Define antes del código: HTTP method/path, entrada (cuerpo, query, path), validación, salida (schema + código), fallos, permisos, paginación y compatibilidad con consumidores existentes. Deja explícita la semántica de `PATCH`/`PUT`, el comportamiento de null frente a campo ausente y claves únicas.

- Router: poco código; `APIRouter(prefix=..., tags=..., dependencies=...)`, `Depends(get_session)`, `response_model`, `status_code`; no contiene SQL ni reglas de negocio complejas.
- Schemas: tipos expresivos, `Field` con restricciones adecuadas, Pydantic v2 `model_config = ConfigDict(from_attributes=True)` para respuestas ORM cuando se requiere.
- Servicio: recibe dependencias explícitas, aplica reglas e invariantes, elige límites de transacción claros; tratar `IntegrityError`/`SQLAlchemyError` con rollback. Evita capturar todo `Exception` para convertirlo silenciosamente en 200.
- Modelos: `Mapped[T]`, `mapped_column`, claves/índices/unicidad reales, import explícito por Alembic. Nunca generar DDL automático en producción.
- Responses: JSON tipado, sin `hash_pwd`, secretos, objetos `AsyncSession` ni tracebacks. Mantén errores sanitizados para el cliente y logs internos con correlación.
- Normalización: usa normalización existente si forma parte del contrato de negocio (en el snapshot `normalize_text` transforma a mayúsculas y elimina diacríticos). No convertir nombres/datos de usuario sin especificación.

## Esqueleto original ilustrativo (no es código copiado del ZIP)

```python
# src/applications/tareas/schemas.py
from pydantic import BaseModel, ConfigDict, Field

class TareaCreate(BaseModel):
    titulo: str = Field(min_length=1, max_length=200)

class TareaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    titulo: str
```

```python
# src/applications/tareas/router.py (adaptar el servicio y permisos reales)
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.manager_db_async import get_session
from core.security import require_roles
from .schemas import TareaCreate, TareaRead
from .controller import TareaService

router = APIRouter(prefix="/tareas", tags=["tareas"],
                   dependencies=[Depends(require_roles("admin"))])

@router.post("/", response_model=TareaRead, status_code=status.HTTP_201_CREATED)
async def crear_tarea(payload: TareaCreate, db: AsyncSession = Depends(get_session)):
    return await TareaService(db).create(payload)
```

El ejemplo **no** es ejecutable hasta escribir/registrar `TareaService`, modelo/migración y tests. No generar endpoints administrativos sin autorización.

## Modificar sin romper compatibilidad

1. Registrar endpoints, schemas, tablas, códigos de estado y cookies existentes antes del cambio.
2. Añadir tests contractuales con fixture aislada y sin secretos reales.
3. Implementar cambios conservadores, y actualizar OpenAPI/documentación.
4. Si es imprescindible alterar un contrato, proponer versionado, período de transición y migraciones explícitas.
