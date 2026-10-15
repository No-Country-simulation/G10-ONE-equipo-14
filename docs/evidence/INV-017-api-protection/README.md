# INV-017 — Protección de la API pública

## Resultado

- Las rutas mutables (`process`, edición, aprobación, rechazo y publicación) usan una dependencia de seguridad común.
- `MUTATIONS_ENABLED=false` bloquea toda escritura con HTTP 403; el Blueprint de Render usa este modo de sólo lectura.
- Cuando `API_WRITE_KEY` está definido, cada escritura exige el encabezado `X-API-Key`; el secreto nunca se registra ni se versiona.
- Las escrituras tienen un límite configurable por IP y devuelven HTTP 429 cuando se excede.
- Health y las consultas GET siguen disponibles sin credenciales.
- El dashboard propaga el secreto únicamente desde la variable de entorno.

## Configuración y alcance

Las variables y las reglas de CORS/rate limiting están descritas en el README principal. El limitador en memoria es adecuado para la única instancia del demo gratuito; una futura arquitectura con réplicas debe usar almacenamiento compartido.

## Verificación

Las pruebas automatizadas cubren el modo sólo lectura, autenticación correcta e incorrecta, rate limiting y propagación del encabezado desde el cliente del dashboard. La validación integral se ejecuta en Docker contra una base PostgreSQL exclusiva de pruebas.

Trazabilidad: GitHub #168 · Jira COMLAB-96.
