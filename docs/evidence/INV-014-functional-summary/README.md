# Evidencia INV-014

Fecha: 14 de octubre de 2026.

El contrato `summary` y el dashboard incluyen:

- sentimiento predominante;
- hasta tres temas principales ordenados por frecuencia;
- tiempo total de procesamiento en milisegundos;
- cantidades recibidas, aceptadas, duplicadas y con errores.

La respuesta completa se persiste, por lo que una repetición idempotente
devuelve exactamente las mismas métricas.

```text
122 passed, 1 warning in 25.16s
```

Trazabilidad: GitHub #159 / Jira COMLAB-93.
