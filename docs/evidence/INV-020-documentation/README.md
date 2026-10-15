# INV-020 — Documentación alineada

## Cambios verificados

- `INTERACTION_TABLE.md` ya no atribuye HTTP 501 a una consulta implementada; documenta 404/409 y la recuperación visual por Run ID.
- `CL-001_BASELINE_AUDIT.md` conserva intacto el valor histórico del diagnóstico de octubre, pero ahora advierte su alcance temporal y registra la resolución verificable de cada hallazgo.
- `ROADMAP_ETAPAS.md` resume el estado real de E1-E8 y reemplaza “E2 es la próxima etapa” por INV-021 a INV-025.
- OCI continúa explícitamente en el alcance final y se mantiene aplazado hasta cerrar el desarrollo no OCI.

## Verificación

Las afirmaciones actuales se contrastaron con los routers, migraciones, workflow de CI, configuración Docker, suite de 130 pruebas y despliegue Render presentes en `main` (`13a0511`). Una búsqueda final comprueba que las menciones a 501 y a E2 como siguiente etapa sólo sobreviven dentro del cuerpo histórico claramente etiquetado de CL-001.

Trazabilidad: GitHub #177 · Jira COMLAB-99.
