# Evidencia INV-010

Fecha: 14 de octubre de 2026.

## Comportamiento verificado

- `PENDING_REVIEW -> APPROVED` y `PENDING_REVIEW -> REJECTED` son las únicas decisiones válidas.
- Repetir una decisión o decidir un activo aprobado/rechazado devuelve HTTP 409 y no crea otra auditoría.
- Editar un activo rechazado crea una versión nueva y lo reabre como `PENDING_REVIEW`.
- Un activo aprobado no puede editarse.
- Publicar dos veces devuelve exactamente el mismo manifest y mantiene un único registro.
- La base de datos impone unicidad de `manifests.asset_id` mediante la migración 005.

## Validación

La suite completa se ejecutó en Docker con PostgreSQL y proveedor de análisis `mock`:

```text
115 passed, 1 warning in 13.89s
```

Trazabilidad: GitHub #147 / Jira COMLAB-89.
