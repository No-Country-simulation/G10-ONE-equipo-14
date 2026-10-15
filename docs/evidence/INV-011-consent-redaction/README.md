# Evidencia INV-011

Fecha: 14 de octubre de 2026.

## Controles verificados

- Consentimiento explícito mediante `publication_consent`.
- Exclusión de publicación mediante `opt_out`.
- Redacción determinística de correos como `[EMAIL]`.
- Redacción determinística de teléfonos como `[PHONE]`.
- Redacción del nombre del autor como `[PERSON]` cuando no existe consentimiento.
- Texto saneado antes de persistirse o enviarse al proveedor de análisis.
- Oportunidad `BLOCKED` y cero activos cuando existe opt-out o PII sensible.

## Validación

```text
117 passed, 1 warning in 23.23s
```

Trazabilidad: GitHub #150 / Jira COMLAB-90.
