# INV-021 — Evidencias visuales E1-E6

Capturas obtenidas el 15 de octubre de 2026 desde la aplicación local iniciada con Docker Compose. No contienen credenciales ni datos personales reales.

## Índice

| Archivo | Etapa | Evidencia |
| --- | --- | --- |
| `01-E1-dashboard-health.png` | E1 | Streamlit operativo, API disponible y PostgreSQL `ok`. |
| `02-E2-openapi-contract.png` | E2 | Contrato OpenAPI v1 real: rutas de ingesta, runs, activos, alertas y publicación. |
| `03-E3-run-analysis.png` | E3 | Run persistido, resumen y análisis real con `gemini-3.1-flash-lite`, prompt versionado y fuente visible. |
| `04-E4-generated-opportunities.png` | E4 | Oportunidades persistidas con tipo, prioridad, reason y reglas de bloqueo. |
| `05-E5-curation-queue.png` | E5 | Cola global recuperada desde PostgreSQL con borrador LinkedIn editable y estado `PENDING_REVIEW`. |
| `06-E6-local-publication-receipt.png` | E6 | Activo aprobado y publicación real/idempotente en almacenamiento local, con object key, content type, SHA-256 y ETag. |

## Recorrido reproducido

- Run ID: `62f117b9-8994-406a-91bf-34d228cb0d2a`
- Entrada: 3 interacciones de demostración con consentimiento.
- Resultado: 3 análisis, 3 oportunidades y 2 activos.
- Activo aprobado/publicado: `f85ba2b1-b63f-424c-a88d-6a74232428df`
- Object key: `one/g10-equipo-14/linkedin/f85ba2b1-b63f-424c-a88d-6a74232428df/v1.json`
- SHA-256/ETag: `cdfe94875b2fb8c0deb44e12b1e4e873d2905781d069ca10c88632b0935231c7`

El recibo E6 se generó desde la respuesta efectiva de `POST /api/v1/assets/{asset_id}/publish` después de aprobar el activo. La repetición devolvió el mismo manifest, comprobando idempotencia. Este recorrido usa `STORAGE_BACKEND=local`; OCI permanece aplazado hasta el despliegue final (INV-002 a INV-005).

## Regeneración

1. Iniciar `docker compose up -d --build`.
2. Procesar tres interacciones de demostración mediante `POST /api/v1/process`.
3. Recuperar el Run ID desde Streamlit y capturar análisis, oportunidades y cola.
4. Aprobar un activo y ejecutar su endpoint `publish`.
5. Verificar object key, SHA-256 y ETag contra el objeto local antes de capturar el recibo.

Trazabilidad: GitHub #180 · Jira COMLAB-100.
