# Seguridad aplicada al proyecto Flask de referencia

## Autenticación de cookies y sesiones

`src/core/security.py` valida JWT firmado (`python-jose`, algoritmo fijado en settings), lee la cookie `X-Sync.Ref`, comprueba `sub` contra tabla `sesiones` y `exp`, obtiene al usuario en tabla `usuarios`, coloca el usuario en `flask.g`. `require_role("admin")` comprueba rol **después** de `require_auth()`. `require_secret_param()` prefiere `X-API-Key`; query `?apikey=` solo legado, no expandir a endpoints nuevos.

- Expiración JWT y expiración de la sesión persistida son comprobaciones distintas: ambas deben cumplirse.
- No devolver token al cliente en el cuerpo de endpoints de consulta ni escribirlo en logs.
- No hacer `DELETE`, limpieza, `commit()` o invalidación silenciosa dentro de las funciones de autenticación; depuración y limpieza van a CLI/job independiente.
- No exponer un registro de administradores anónimo: `/login/register` requiere sesión válida y rol `admin`; el primer admin se crea mediante `create-admin` fuera de HTTP.
- Evitar enumeración de usuarios: credenciales incorrectas deben producir errores uniformes; no loguear contraseñas ni secretos.

## Cookies, CSRF y CORS

- Cookie: `httponly=True`, `secure` controlado por `COOKIE_SECURE` (producción HTTPS = `True`), `samesite="Lax"`, `path="/"`; revisar compatibilidad con frontend cuando cambien estos atributos.
- La autenticación por **cookie** no equivale a protección CSRF. Antes de publicar endpoints que cambian estado, usar defensas adecuadas (tokens CSRF/validación de origen y cabeceras, según arquitectura) y tests de ataques cruzados. `SameSite` ayuda, pero no es defensa universal por sí sola.
- Si `BACKEND_CORS_ORIGINS` está vacío, la app no aplica la extensión CORS; para credenciales usar lista explícita de orígenes y `supports_credentials=True`. **No** combinar credenciales con comodín de orígenes.
- Guardar secretos fuera de VCS, config por variables de entorno, no imprimir URLs de DB con contraseña, desactivar debug en producción.
- Proteger `POST /login/` con controles antibruteforce y revisar política de roles/atributos permitidos al registrar; el backend de referencia **no** debe presentarse como completamente securizado para producción.

## Decoradores y errores

Orden para vistas que acceden a DB: `@require_db_session` exterior a `@require_auth()`; luego `@require_role`. Fallos esperados: `401` no autenticado, `403` autenticado sin permiso, `409` conflicto al registrar. Evitar cambiar `401` por `403` sin revisar contrato.

## Evaluación necesaria

Pruebas: sin cookie 401; JWT firmado inválido 401; sesión persistida ausente/caducada 401 y **sin borrarla**; usuario sin permisos 403; admin autorizado 201; claves API ausentes/incorrectas 401; CORS orígenes maliciosos rechazados; cookies con `HttpOnly`, `Secure` cuando proceda y `SameSite`; CSRF para mutaciones autenticadas. Distinguir pruebas que existen de pruebas propuestas.

Referencias: https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html ; https://flask.palletsprojects.com/en/stable/security/ ; https://flask-cors.readthedocs.io/en/latest/api.html
