# Evidencia INV-013

Fecha: 14 de octubre de 2026.

## Comportamiento verificado

- El sentimiento negativo crea una alerta interna persistente.
- La oportunidad asociada queda `BLOCKED`.
- No se generan activos LinkedIn ni FAQ.
- `GET /api/v1/alerts?status=OPEN` recupera la alerta.
- Streamlit presenta una pestaña separada **Alertas internas**.

## Validación

```text
122 passed, 1 warning in 16.38s
```

La pestaña **Alertas internas** fue comprobada visualmente en la aplicación
local, con API y PostgreSQL saludables.

Trazabilidad: GitHub #156 / Jira COMLAB-92.
