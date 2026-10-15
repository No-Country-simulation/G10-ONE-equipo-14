# Evidencia INV-015

Fecha: 15 de octubre de 2026.

## Eventos estructurados

- `request_completed` y `request_failed`: método, ruta, estado, request ID y duración.
- `analysis_completed` y `analysis_retry`: proveedor, intento, duración y tipo de error.
- `analysis_fallback_failed`: proveedor alternativo y tipo de error.
- `storage_put_completed`: backend, bucket, bytes y duración.

El formato es JSON y omite texto de interacciones, contenido generado y mensajes
de excepciones externas. Una prueba introduce deliberadamente correo sensible
en una excepción y comprueba que no aparece en ningún evento.

```text
126 passed, 1 warning in 15.69s
```

Trazabilidad: GitHub #165 / Jira COMLAB-95.
