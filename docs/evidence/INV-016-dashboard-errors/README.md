# Evidencia INV-016

Fecha: 14 de octubre de 2026.

Se verificó el manejo controlado de:

- detalles HTTP de FastAPI;
- errores de validación 422;
- conflictos 409;
- timeouts;
- fallas de conexión;
- respuestas no JSON.

Todos los flujos visuales capturan `requests.RequestException` y mantienen la
sesión de Streamlit operativa.

```text
124 passed, 1 warning in 16.80s
```

Trazabilidad: GitHub #162 / Jira COMLAB-94.
