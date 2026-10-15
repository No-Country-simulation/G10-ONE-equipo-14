# Evidencia INV-023 — procesamiento asíncrono

Fecha: 15 de octubre de 2026.

## Decisión basada en mediciones

Se procesó tres veces el máximo contractual de 500 interacciones contra la API
local y PostgreSQL. Cada ejecución produjo 500 análisis, 500 oportunidades y
500 activos, sin errores ni duplicados.

| Ejecución | Run ID | Tiempo HTTP | Tiempo reportado por API | Resultado frente a 30 s |
| --- | --- | ---: | ---: | --- |
| 1 | `a0725bb7-abc5-4e9c-9cc2-20e4838763cd` | 15,105 s | 14,880 s | Cumple |
| 2 | `39e037dc-f2a5-4995-9b08-7b0ee16842c0` | 64,337 s | 63,760 s | No cumple |
| 3 | `68aeac3b-6b73-4611-8c13-7aa159e8a517` | 47,762 s | 46,404 s | No cumple |

El objetivo no se cumplió de forma estable, por lo que se implementó la cola
prevista en el criterio de cierre, en lugar de ocultar la variación con una sola
medición favorable.

## Implementación

- `POST /api/v1/process/async` valida y encola el contrato completo.
- La idempotencia tiene alcance organización/comunidad y detecta reutilización
  de la clave con un payload diferente.
- PostgreSQL conserva payload, hash, estado, intentos, timestamps, error seguro
  y `run_id`; no se depende de memoria del proceso.
- El worker usa `FOR UPDATE SKIP LOCKED`, de modo que varios workers no reclamen
  el mismo trabajo.
- `GET /api/v1/jobs/{job_id}` permite consultar el resultado sin mantener abierta
  la conexión original.
- La API ejecuta las migraciones y el worker espera su health check, evitando una
  carrera de migraciones durante `docker compose up`.

## Verificación final

Con `ANALYSIS_PROVIDER=mock` para obtener una medición determinística:

```json
{
  "job_id": "6cf2d5a8-58e1-4ca6-bbd4-31a31d69ea87",
  "run_id": "31140925-9582-4445-ba27-2e63ca2d0a94",
  "count": 500,
  "enqueue_seconds": 0.062,
  "completion_seconds": 19.841,
  "target_enqueue_seconds": 1.0,
  "target_met": true,
  "attempts": 1
}
```

La cola desacopla el tiempo de respuesta del trabajo: los 500 registros se
aceptaron en 62 ms y el procesamiento terminó durablemente en un único intento.
Las pruebas automatizadas cubren migración/downgrade, replay, conflicto, consulta,
éxito del worker y persistencia de fallo seguro.
