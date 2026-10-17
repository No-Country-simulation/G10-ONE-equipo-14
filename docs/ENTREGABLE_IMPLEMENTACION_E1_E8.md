# Entregable técnico e implementación de CommunityLab (E1–E8)

Fecha de actualización y verificación: 17 de octubre de 2026.

Este documento permite a otra persona descargar, ejecutar, verificar y continuar CommunityLab. También registra qué se implementó en cada etapa y qué evidencia visual existe realmente.

## 1. Resultado entregado

CommunityLab es un MVP operativo que recibe interacciones JSON, CSV o webhook,
normaliza y deduplica los datos, protege información sensible, ejecuta análisis
mock o Gemini, detecta oportunidades y alertas, genera activos LinkedIn/FAQ y
permite curarlos antes de publicarlos mediante un adaptador de almacenamiento.
Los lotes grandes disponen además de una cola asíncrona durable.

Entorno público de demostración:

- Dashboard: https://communitylab-dashboard.onrender.com
- API: https://communitylab-api.onrender.com
- OpenAPI: https://communitylab-api.onrender.com/docs
- Health: https://communitylab-api.onrender.com/api/v1/health

El despliegue público usa Render Free en modo de solo lectura. Puede tardar
cerca de un minuto en reactivarse después de permanecer inactivo y la base
PostgreSQL gratuita debe recrearse o migrarse al vencer el período ofrecido por
el proveedor.

## 2. Implementación por etapas

| Etapa | Resultado implementado | Referencia principal | Evidencia visual versionada |
| --- | --- | --- | --- |
| E1 | Base del proyecto, contratos FastAPI, Streamlit, Docker Compose y CI | `app/`, `dashboard/`, `docker-compose.yml`, `.github/workflows/` | `INV-021-visual-evidence/01-E1-dashboard-health.png` |
| E2 | Modelo persistente, migraciones, relaciones, triggers y consulta por Run ID | `app/db/models/`, `alembic/versions/` | `INV-021-visual-evidence/02-E2-openapi-contract.png` |
| E3 | Pipeline mock/Gemini, PII, oportunidades, alertas, resiliencia y grounding | `app/services/`, `app/ai/` | `INV-021-visual-evidence/03-E3-run-analysis.png` |
| E4 | Generación y versionado de contenido LinkedIn/FAQ con fuentes | `app/services/content_generation.py`, `asset_generation.py` | `INV-021-visual-evidence/04-E4-generated-opportunities.png` |
| E5 | Cola, edición, aprobación y rechazo persistentes | `app/api/v1/endpoints/assets.py`, `dashboard/` | `INV-021-visual-evidence/05-E5-curation-queue.png` |
| E6 | Adaptador OCI/local, publicación idempotente, manifiestos y hashes | `app/services/object_storage.py` | `INV-021-visual-evidence/06-E6-local-publication-receipt.png` |
| E7 | E2E, observabilidad, backup, benchmark, evaluación y 159 pruebas | `tests/`, `scripts/`, `docs/evidence/` | Evidencias E1–E6, Swagger y health |
| E8 | Render, PostgreSQL, HTTPS, protección pública y dashboard renovado | `render.yaml`, Dockerfiles, `dashboard/` | `E8-render-deployment/` y verificación pública del 17/10/2026 |

## 3. Instalación local paso a paso

### Requisitos

- Git.
- Docker Desktop con Docker Compose v2.
- Puertos `8000` y `8501` disponibles.

### Descarga y configuración

```powershell
git clone https://github.com/No-Country-simulation/G10-ONE-equipo-14.git
Set-Location G10-ONE-equipo-14
Copy-Item .env.example .env
```

No se deben copiar al repositorio claves, tokens, `.env` ni el archivo privado de OCI.

### Construcción e inicio

```powershell
docker compose up -d --build
docker compose ps
```

Al iniciar, PostgreSQL pasa su health check, la API aplica `alembic upgrade head` y luego se inicia Streamlit.

Abrir:

- Dashboard: http://localhost:8501
- OpenAPI: http://localhost:8000/docs
- Health: http://localhost:8000/api/v1/health

### Prueba funcional

1. Abrir el dashboard.
2. Cargar `data/sample_interactions.csv`.
3. Presionar **Procesar archivo**.
4. Confirmar que se muestren análisis, oportunidades y activos sin errores.
5. Revisar un activo, editarlo si corresponde y aprobarlo o rechazarlo.
6. Repetir la carga para comprobar deduplicación e idempotencia.

### Pruebas automatizadas

```powershell
docker compose exec db createdb -U communitylab communitylab_test
docker compose exec -e TEST_DATABASE_URL=postgresql+psycopg://communitylab:communitylab@db:5432/communitylab_test api python -m pytest -q tests
```

Si la base de pruebas ya existe, se puede omitir el primer comando. En el cierre
del 17 de octubre de 2026 se obtuvieron **159 pruebas aprobadas**. El CI ejecuta
además Ruff, verificación de formato, `pip-audit`, compilación del dashboard,
migraciones, Terraform y smoke tests públicos.

### Detención y diagnóstico

```powershell
docker compose logs --tail 100 db api dashboard
docker compose down
```

`docker compose down` conserva los datos. `docker compose down -v` elimina el volumen y sólo debe usarse si los datos se pueden descartar.

## 4. Cómo se implementó y publicó

1. Cada etapa se planificó mediante issues de GitHub y tickets Jira relacionados.
2. El código se desarrolló en ramas cortas y se integró mediante pull requests.
3. Las tablas y triggers se gestionaron con migraciones Alembic reproducibles.
4. Cada servicio se validó con pruebas unitarias, integración y E2E.
5. `develop` se utilizó para integración y `main` para la versión estable.
6. Render consume `render.yaml`, construye la API y el dashboard con Docker y conecta PostgreSQL mediante una variable privada.
7. La API ejecuta las migraciones antes de levantar Uvicorn.
8. Los endpoints públicos HTTPS y el recorrido CSV completo se verificaron después del despliegue.

Para continuar el proyecto, consultar `CONTRIBUTING.md`, `docs/GIT_WORKFLOW.md` y `docs/ROADMAP_ETAPAS.md`.

## 5. Evidencias visuales

Las imágenes se encuentran dentro de `docs/evidence/`:

```text
docs/evidence/
├── COMLAB-115-dashboard-ux/  # recorrido visual renovado, paso a paso
├── INV-021-visual-evidence/   # capturas reales E1–E6
├── E7-cierre-mvp/            # Swagger y health
├── E8-render-deployment/     # dashboard y OpenAPI públicos
├── INV-023-async-benchmark/  # resultado del lote de 500
└── INV-024-quality-evaluation/ # evaluación reproducible
```

El índice y procedimiento para regenerar las capturas E1–E6 se encuentran en
[`evidence/INV-021-visual-evidence/README.md`](evidence/INV-021-visual-evidence/README.md).
El recorrido renovado, con cada captura visible y explicada, se encuentra en
[`evidence/COMLAB-115-dashboard-ux/README.md`](evidence/COMLAB-115-dashboard-ux/README.md).
Las evidencias no contienen secretos ni datos personales reales.

## 6. Trazabilidad de este entregable

- GitHub: [issue #122](https://github.com/No-Country-simulation/G10-ONE-equipo-14/issues/122)
- Jira: [COMLAB-81](https://g10-latam-equipo14.atlassian.net/browse/COMLAB-81)
- Release E1–E8 inicial: PR #121.
- Cierre funcional no OCI: consultar `INVENTARIO_PROYECTO.md`.
- Dashboard y ayuda contextual: PR #220.
- Release verificado en producción: PR #221, commit `3496f4c` y CI
  [#38999088448](https://github.com/No-Country-simulation/G10-ONE-equipo-14/actions/runs/38999088448).

## 7. Límites conocidos

- La demostración pública usa el plan gratuito de Render.
- PostgreSQL Free debe recrearse o migrarse antes de su vencimiento.
- El adaptador OCI está implementado, pero la activación integral del bucket,
  layout, `manifest.json` y recibo visual continúa pendiente en INV-002 a INV-005.
- El despliegue Render usa almacenamiento local efímero y no debe confundirse
  con persistencia permanente de archivos.
- Las credenciales OCI permanecen fuera de Git.
