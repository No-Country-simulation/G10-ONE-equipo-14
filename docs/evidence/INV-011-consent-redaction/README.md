# Evidencia INV-011

Fecha: 14 de octubre de 2026.

## Controles verificados

- Consentimiento explícito mediante `publication_consent`.
- Exclusión de publicación mediante `opt_out`.
- Redacción determinística de correos como `[EMAIL]`.
- Redacción determinística de teléfonos como `[PHONE]`.
- Redacción del nombre del autor como `[PERSON]` en todos los borradores.
- Texto saneado antes de persistirse o enviarse al proveedor de análisis.
- Oportunidad `BLOCKED` y cero activos cuando existe opt-out. Correos, teléfonos y menciones de usuario se redactan antes de crear borradores.

## Validación

```text
117 passed, 1 warning in 23.23s
```

Trazabilidad: GitHub #150 / Jira COMLAB-90.
