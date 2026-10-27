# Seguridad, autenticación y autorización

Referencia original: [`src/core/security.py`](../examples/backend_async/src/core/security.py), [`login/router.py`](../examples/backend_async/src/applications/login/router.py), [`login/controller.py`](../examples/backend_async/src/applications/login/controller.py).

- JWT firmado lleva `sub`, `iat`, `exp`; cookie `X-Sync.Ref` es HttpOnly, SameSite=Lax y `Secure` según configuración.
- `@require_auth` consulta con `await` la sesión persistida y el usuario, verificando su vigencia. No elimina registros expirados desde la ruta HTTP. Los roles (`@require_role('admin')`) se validan **después** de autenticación.
- `POST /login/register` requiere admin; no reabrir registro público. El administrador inicial se crea con CLI.
- `GET /users/users` exige cookie y API key; usar header `X-API-Key`. El parámetro `?apikey=` está solo por compatibilidad y puede filtrarse en logs: **no copiarlo a endpoints nuevos**.
- Contratos HTTP de auth: probar 401 sin cookie, 403 sin rol y 409 usuario duplicado, expiración JWT/sesión, cookie correcta y prohibición de DELETE en autenticación.
- **Pendientes de seguridad de la referencia**, no fingir que están resueltos: controles anti-CSRF para escrituras con cookies, rate limiting del login, política de contraseñas y roles, rotación de secretos y configuración CORS. SameSite no basta en todos los escenarios CSRF.

`asyncio.to_thread` en controller evita bloquear el loop al generar/comprobar hashes. Revisar versiones de bibliotecas y no exponer secretos en logs.
