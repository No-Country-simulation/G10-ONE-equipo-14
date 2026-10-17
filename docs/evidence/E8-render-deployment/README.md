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

## Revalidación del 17 de octubre de 2026

- Release de producción: PR #221, commit `3496f4c`.
- CI [#38999088448](https://github.com/No-Country-simulation/G10-ONE-equipo-14/actions/runs/38999088448):
  calidad, **159 pruebas**, Terraform y smoke público aprobados.
- Dashboard comprobado en navegador con la nueva identidad visual y la ayuda
  contextual de Organización, Comunidad y Período de referencia.
- API y PostgreSQL mostraron estado operativo y no se registraron errores de
  consola en la comprobación.

La cifra de 93 pruebas anterior se conserva como evidencia histórica del cierre
original E8; 159 es la cifra vigente de la entrega actual.

## Evidencias

- `01-dashboard-publico.png`: captura renovada el 17 de octubre de 2026 del
  dashboard HTTPS con la nueva identidad y los servicios API/PostgreSQL
  operativos.
- `02-api-swagger.png`: documentación OpenAPI pública.

El recorrido completo de interfaz está documentado en
[`../COMLAB-115-dashboard-ux/README.md`](../COMLAB-115-dashboard-ux/README.md).

## Límites del plan de demostración

Los servicios gratuitos pueden suspenderse por inactividad y tardar aproximadamente un minuto en reactivarse. La base PostgreSQL Free de Render expira a los 30 días; este despliegue es exclusivamente para demostración escolar y debe recrearse o migrarse antes del vencimiento.
