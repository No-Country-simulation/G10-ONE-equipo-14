# CL-001 - Auditoría de la base existente

Fecha: 2026-10-01  
Rama base: `develop`  
Commit auditado: `b5a6bbe`  
Alcance: `app/`, `dashboard/`, `alembic/`, `tests/`, Docker, CI y documentación operativa.

## Resultado ejecutivo

El repositorio contiene más que un esqueleto: hay contratos v1, ingesta JSON/CSV, normalización, deduplicación, persistencia de interacciones e idempotencia. Sin embargo, la aplicación no puede importarse ni ejecutar su suite de pruebas en el estado auditado. La prioridad antes de desarrollar nuevas funcionalidades es estabilizar la base.

No se encontraron triggers de PostgreSQL. Las migraciones actuales crean las tablas `interactions` y `runs`, sus restricciones e índices.

## Inventario y decisión

| Componente | Estado observado | Decisión recomendada |
|---|---|---|
| `app/schemas/v1/` | Contratos versionados para interacciones, análisis, oportunidades, activos, aprobaciones y manifest | Conservar como contrato vigente; corregir sólo mediante cambios compatibles o una versión nueva |
| `app/api/v1/` | Health e ingesta implementados; runs y curaduría mayormente scaffolding | Conservar y estabilizar; mantener `501` mientras una operación no esté implementada |
| `app/services/` | Ingesta e idempotencia sustanciales; `mock_pipeline.py` obsoleto | Conservar ingesta/idempotencia después de pruebas; retirar o actualizar el mock |
| `app/db/` | Modelos de interacciones y runs con error de nombre/importación | Corregir antes de cualquier desarrollo adicional |
| `alembic/` | Dos migraciones explícitas; registro de modelos incompleto | Conservar migraciones compartidas; corregir registro y agregar cambios futuros en revisiones nuevas |
| `dashboard/` | Pantalla mínima de health, no el recorrido visual del MVP | Conservar como punto de partida para CL-003 |
| `tests/` | Cobertura diseñada para contratos, ingesta e idempotencia; no puede recolectarse | Conservar y reparar infraestructura de ejecución |
| Docker Compose | Define API, dashboard y PostgreSQL | Conservar; hacer reproducibles migraciones y base de pruebas |
| `backend/` y `frontend/` | Carpetas vacías con `.gitkeep` | No usar como estructura paralela; retirar en un cambio acordado o documentarlas como reservadas |

## Hallazgos

### P0 - La aplicación no puede importarse

El archivo existente es `app/db/models/interactions.py`, pero el código importa `app.db.models.interaction` desde:

- `app/db/models/__init__.py`
- `app/services/ingestion.py`
- `tests/conftest.py`
- `tests/test_ingestion.py`
- `tests/test_idempotency.py`

Resultado reproducido:

```text
ModuleNotFoundError: No module named 'app.db.models.interaction'
```

Impacto: FastAPI, Alembic y pytest quedan bloqueados antes de iniciar.

### P0 - CI falla antes de recolectar pruebas

El workflow ejecuta `pytest -q` y GitHub Actions no encuentra el paquete `app`:

```text
ModuleNotFoundError: No module named 'app'
```

Todos los runs recientes inspeccionados fallan. Usar `python -m pytest` o instalar el proyecto resuelve solamente esta primera capa; después seguirían el error de `interaction` y la falta de PostgreSQL de pruebas.

Impacto: los pull requests no tienen una señal de calidad utilizable.

### P0 - Las reglas de exclusión no están activas

El repositorio tiene un archivo llamado `gitignore`, sin el punto inicial requerido por Git. En consecuencia, `.env`, `__pycache__`, temporales, entornos virtuales y otros archivos sensibles o generados no están realmente ignorados.

No se encontraron secretos actualmente versionados con los patrones revisados, pero el riesgo de incorporarlos accidentalmente es alto.

### P1 - La suite requiere una base que CI y Compose no crean

`tests/conftest.py` intenta conectarse a `communitylab_test` y crea/elimina tablas para toda la sesión. El workflow no declara un servicio PostgreSQL. Docker Compose crea solamente la base configurada en `POSTGRES_DB`, normalmente `communitylab`, y no crea `communitylab_test`.

Impacto: aun corrigiendo imports, la suite completa no puede ejecutarse de forma reproducible.

### P1 - El arranque no aplica migraciones

`start.ps1` copia `.env` y ejecuta `docker compose up --build`, pero no ejecuta `alembic upgrade head`. Una base nueva puede estar saludable y, al mismo tiempo, carecer de `interactions` y `runs`.

Impacto: health puede responder correctamente mientras `/process` falla por tablas inexistentes.

### P1 - Alembic no registra todos los modelos

`alembic/env.py` importa `app.db.models`, cuyo `__init__.py` exporta solamente `Interaction` y además usa el nombre de módulo incorrecto. `Run` no se registra mediante ese import.

Impacto: la metadata usada para autogenerar o comparar migraciones queda incompleta.

### P1 - `mock_pipeline.py` está roto y desactualizado

El módulo importa `app.schemas.process`, ruta que no existe, y construye una respuesta con el campo `storage`, que no pertenece a `ProcessResponse` v1. Actualmente no está conectado al router.

Impacto: cualquier importación o reutilización futura falla y genera confusión sobre el contrato vigente.

### P2 - Documentación operativa desactualizada

- `docs/INTERACTION_TABLE.md` afirma que `/process` es un mock que no persiste, pero el endpoint actual sí ejecuta ingesta e idempotencia.
- `README.md` presenta `backend/` y `frontend/` como estructura principal, mientras el código vive en `app/` y `dashboard/`.
- `README.md` remite a `docs/CONTRIBUTING.md`, pero el archivo está en la raíz.

Impacto: una persona nueva puede trabajar en carpetas equivocadas o asumir un estado falso.

### P2 - El estado de runs no coincide con el scaffolding expuesto

`POST /process` ya persiste `Run` y su respuesta idempotente, pero `GET /runs/{run_id}` continúa devolviendo `501` con un mensaje que dice que la persistencia de runs pertenece a una fase futura.

Impacto: el mensaje de error y la documentación no representan el estado real.

### P2 - Validación por registro no es uniforme

CSV captura errores por fila. JSON usa un `ProcessRequest` que valida el lote completo antes de entrar al endpoint, por lo que una interacción inválida puede rechazar toda la solicitud en lugar de aparecer en `record_errors`.

Impacto: no se cumple de la misma manera el objetivo de mostrar errores por registro para ambos formatos.

### P3 - Los triggers aún no tienen casos de uso aprobados

No hay funciones ni triggers SQL. Los candidatos planteados - `updated_at`, auditoría de cambios de estado e historial de aprobaciones - dependen primero del modelo de datos de CL-002.

Decisión: no implementar triggers hasta aprobar tablas, eventos, comportamiento transaccional y pruebas esperadas.

## Verificaciones ejecutadas

| Verificación | Resultado |
|---|---|
| `python -m compileall -q app alembic tests` | Correcto: no se encontraron errores de sintaxis |
| `pytest --collect-only -q` con dependencias aisladas | Falló por `app.db.models.interaction` inexistente |
| GitHub Actions, runs recientes | Fallan antes de recolectar por `No module named 'app'` |
| `docker compose --env-file .env.example config --quiet` | Falló porque `docker-compose.yml` exige un archivo `.env` adicional |
| `docker build` | No ejecutado: Docker Desktop está instalado pero el daemon no estaba activo |
| Búsqueda de triggers | No se encontraron triggers ni `CREATE TRIGGER` |
| Búsqueda básica de secretos versionados | No se encontraron coincidencias; la ausencia de `.gitignore` funcional sigue siendo un riesgo |

## Orden recomendado de corrección

1. [CL-010](https://github.com/No-Country-simulation/G10-ONE-equipo-14/issues/44): restaurar `.gitignore` y limpiar artefactos locales no versionados.
2. [CL-011](https://github.com/No-Country-simulation/G10-ONE-equipo-14/issues/45): unificar el nombre del modelo `interaction`, reparar imports y registrar todos los modelos SQLAlchemy para Alembic.
3. [CL-012](https://github.com/No-Country-simulation/G10-ONE-equipo-14/issues/46): hacer reproducible CI con import path, PostgreSQL y base aislada de pruebas.
4. [CL-013](https://github.com/No-Country-simulation/G10-ONE-equipo-14/issues/47): automatizar o documentar de manera inequívoca la aplicación de migraciones.
5. [CL-014](https://github.com/No-Country-simulation/G10-ONE-equipo-14/issues/48): retirar o actualizar `mock_pipeline.py` y alinear README, guías y mensajes `501` con el comportamiento real.
6. Ejecutar la suite completa antes de iniciar CL-002, CL-003 o CL-004.

## Conclusión

La arquitectura base es recuperable y no conviene reiniciarla en carpetas nuevas. Debe estabilizarse mediante correcciones pequeñas y verificables. Hasta que los P0 y P1 estén resueltos, no se recomienda agregar tablas, triggers, interfaz completa ni pipeline de IA.
