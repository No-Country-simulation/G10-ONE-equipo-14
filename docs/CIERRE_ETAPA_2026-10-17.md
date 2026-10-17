# Acta de cierre temporal de CommunityLab

Fecha de corte: 17 de octubre de 2026.

## Estado declarado

CommunityLab queda cerrado por ahora como **MVP funcional no OCI, documentado y
desplegado en Render**. La aplicación pública, la API y PostgreSQL respondieron
correctamente después de la publicación del commit `3496f4c` en `main`.

Este cierre no declara completa la integración final con OCI. Los cuatro puntos
INV-002 a INV-005 permanecen abiertos, identificados y fuera del alcance de este
corte hasta disponer de credenciales, permisos y una ventana de despliegue OCI.

## Resultado disponible

- Dashboard público: https://communitylab-dashboard.onrender.com
- API: https://communitylab-api.onrender.com
- OpenAPI: https://communitylab-api.onrender.com/docs
- Health: https://communitylab-api.onrender.com/api/v1/health
- Manual de usuario: [`MANUAL_USUARIO.md`](MANUAL_USUARIO.md)
- Prueba funcional: [`sets_pruebas/GUIA_PRUEBA_FUNCIONAL.md`](sets_pruebas/GUIA_PRUEBA_FUNCIONAL.md)
- Entregable técnico: [`ENTREGABLE_IMPLEMENTACION_E1_E8.md`](ENTREGABLE_IMPLEMENTACION_E1_E8.md)
- Inventario y brechas: [`INVENTARIO_PROYECTO.md`](INVENTARIO_PROYECTO.md)

## Verificación final

| Control | Resultado |
| --- | --- |
| Pruebas automatizadas | 159 aprobadas |
| Calidad y formato | Ruff aprobado |
| Dependencias | `pip-audit` aprobado |
| Migraciones | upgrade/downgrade aprobado en PostgreSQL de pruebas |
| Infraestructura | Terraform validado |
| Smoke público | API y dashboard aprobados |
| Revisión en navegador | Nueva interfaz y ayuda visibles, sin errores de consola |
| CI de producción | [GitHub Actions #38999088448](https://github.com/No-Country-simulation/G10-ONE-equipo-14/actions/runs/38999088448) |

La entrega visual y de ayuda se integró mediante el PR
[#220](https://github.com/No-Country-simulation/G10-ONE-equipo-14/pull/220) y
se publicó mediante el PR
[#221](https://github.com/No-Country-simulation/G10-ONE-equipo-14/pull/221).

## Alcance cerrado

- Ingesta JSON, CSV y webhook.
- Normalización, deduplicación e idempotencia.
- Persistencia PostgreSQL y consulta por Run ID.
- Análisis mock/Gemini, grounding, privacidad y fallback explícito.
- Oportunidades, alertas internas y activos LinkedIn/FAQ trazables.
- Curaduría persistente con edición, aprobación y rechazo.
- Procesamiento asíncrono durable para lotes grandes.
- Publicación idempotente mediante adaptador local/OCI.
- Observabilidad, protección de mutaciones, backup y restauración.
- Dashboard con identidad visual, ayuda contextual y datos de solo lectura
  diferenciados de los controles funcionales.
- CI, evaluación de calidad, benchmark y evidencias reproducibles.

## Pendientes deliberados para reabrir el proyecto

1. **INV-002 / GitHub #195 / COMLAB-105:** activar OCI Object Storage.
2. **INV-003 / GitHub #196 / COMLAB-106:** completar el layout obligatorio.
3. **INV-004 / GitHub #197 / COMLAB-107:** persistir y verificar `manifest.json`.
4. **INV-005 / GitHub #198 / COMLAB-108:** publicar desde Streamlit y mostrar el recibo OCI.

Además, antes de distribuir el proyecto fuera del equipo se debe elegir y
agregar una licencia. La base gratuita de Render debe vigilarse y migrarse o
recrearse si el proveedor anuncia su vencimiento.

## Cómo retomar

1. Leer este documento y `INVENTARIO_PROYECTO.md`.
2. Confirmar acceso autorizado a OCI sin guardar secretos en Git.
3. Tomar INV-002 y crear una rama corta desde `develop`.
4. Continuar INV-003, INV-004 e INV-005 en ese orden.
5. Repetir pruebas, evidencias, backup y smoke tests antes de un nuevo release.

Los archivos locales no versionados `docs/Detalle_proyecto.pdf` y
`docs/Prueba.csv` no forman parte de este cierre y se conservaron sin cambios.
