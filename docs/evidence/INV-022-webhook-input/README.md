# INV-022 — Entrada automática por webhook

## Resultado

- Nuevo `POST /api/v1/webhooks/interactions` con contrato v1 neutral al proveedor.
- `source + event_id` determina external ID e idempotencia de extremo a extremo.
- El adaptador reutiliza `_response`: normalización, persistencia, análisis, oportunidades, activos, alertas y respuesta son los mismos que para carga manual.
- La dependencia común de seguridad protege el endpoint con interruptor, clave API y rate limiting.
- `docs/WEBHOOK_INTEGRATION.md` documenta n8n, Discord, Slack, consentimiento, firma del proveedor y manejo de reintentos.

## Verificación

Las pruebas comprueban procesamiento, external ID derivado, replay con el mismo run, conflicto si un proveedor reutiliza el ID con contenido distinto y bloqueo cuando las mutaciones están deshabilitadas. La suite integral se ejecuta contra PostgreSQL aislado.

Trazabilidad: GitHub #183 · Jira COMLAB-101.
