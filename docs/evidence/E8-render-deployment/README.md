# E8 — Despliegue gratuito en Render

Fecha de validación: 2026-10-07.

## Servicios publicados

- Dashboard: https://communitylab-dashboard.onrender.com
- API: https://communitylab-api.onrender.com
- OpenAPI: https://communitylab-api.onrender.com/docs
- Health: https://communitylab-api.onrender.com/api/v1/health
- PostgreSQL administrado: `communitylab-db` (plan Free de Render)

## Pruebas realizadas

- Health HTTPS con API y PostgreSQL en estado `ok`.
- Carga pública de `data/sample_interactions.csv`.
- Run `fec85af3-76d6-43e7-acb8-11d28b3d981f`: estado `ACCEPTED`.
- Resultado: 20 análisis, 15 oportunidades, 20 activos y 0 errores.
- Suite automatizada: 93 pruebas aprobadas y 1 omitida.

## Evidencias

- `01-dashboard-publico.png`: dashboard HTTPS conectado a la API y PostgreSQL.
- `02-api-swagger.png`: documentación OpenAPI pública.

## Límites del plan de demostración

Los servicios gratuitos pueden suspenderse por inactividad y tardar aproximadamente un minuto en reactivarse. La base PostgreSQL Free de Render expira a los 30 días; este despliegue es exclusivamente para demostración escolar y debe recrearse o migrarse antes del vencimiento.
