# Entregable técnico e implementación de CommunityLab (E1–E8)

Fecha de cierre: 7 de octubre de 2026.

Este documento permite a otra persona descargar, ejecutar, verificar y continuar CommunityLab. También registra qué se implementó en cada etapa y qué evidencia visual existe realmente.

## 1. Resultado entregado

CommunityLab es un MVP que recibe interacciones JSON o CSV, normaliza y deduplica los datos, los procesa mediante un pipeline de análisis, detecta oportunidades, genera activos LinkedIn/FAQ, permite curarlos y publica activos aprobados mediante un adaptador de almacenamiento.

Entorno público de demostración:

- Dashboard: https://communitylab-dashboard.onrender.com
- API: https://communitylab-api.onrender.com
- OpenAPI: https://communitylab-api.onrender.com/docs
- Health: https://communitylab-api.onrender.com/api/v1/health

El despliegue público usa Render Free. Puede tardar cerca de un minuto en reactivarse después de permanecer inactivo y la base PostgreSQL gratuita expira a los 30 días.

## 2. Implementación por etapas

| Etapa | Resultado implementado | Referencia principal | Evidencia visual versionada |
| --- | --- | --- | --- |
| E1 | Base del proyecto, contratos FastAPI, Streamlit, Docker Compose y CI | `app/`, `dashboard/`, `docker-compose.yml`, `.github/workflows/` | No se tomó una captura propia de la etapa |
| E2 | Modelo persistente, migraciones, relaciones y triggers de `updated_at` | `app/db/models/`, `alembic/versions/003_*`, `004_*` | No se tomó una captura propia de la etapa |
| E3 | Pipeline de análisis, PII, oportunidades, resiliencia e integración | `app/services/analysis.py`, `pipeline.py`, `pii_detection.py` | No se tomó una captura propia de la etapa |
| E4 | Generación y versionado de contenido LinkedIn/FAQ | `app/services/content_generation.py`, `asset_generation.py` | No se tomó una captura propia de la etapa |
| E5 | Consulta, edición, aprobación y rechazo persistentes | `app/api/v1/endpoints/assets.py`, dashboard Streamlit | No se tomó una captura propia de la etapa |
| E6 | Adaptador OCI/local, publicación, manifiestos y hashes | `app/services/object_storage.py` | No se tomó una captura propia de la etapa |
| E7 | Integración MVP, pruebas E2E, Swagger y health | `tests/test_e2e_mvp.py`, `docs/evidence/E7-cierre-mvp/` | Swagger y health |
| E8 | Blueprint Render, PostgreSQL administrado, HTTPS y demo pública | `render.yaml`, Dockerfiles, `docs/evidence/E8-render-deployment/` | Dashboard público y Swagger público |

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

Si la base de pruebas ya existe, se puede omitir el primer comando. En el cierre E8 se obtuvieron 93 pruebas aprobadas y 1 omitida.

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
├── E7-cierre-mvp/
│   ├── 02-swagger.png
│   └── 03-health.png
└── E8-render-deployment/
    ├── 01-dashboard-publico.png
    └── 02-api-swagger.png
```

No existen capturas versionadas de E1 a E6. Esas etapas se verifican actualmente mediante código, migraciones, pruebas y trazabilidad de issues/PR. Si el equipo exige una captura por etapa, deben recrearse retrospectivamente en una ejecución local y guardarse en carpetas `docs/evidence/E1-*` a `E6-*` sin incluir secretos ni datos personales.

## 6. Trazabilidad de este entregable

- GitHub: [issue #122](https://github.com/No-Country-simulation/G10-ONE-equipo-14/issues/122)
- Jira: [COMLAB-81](https://g10-latam-equipo14.atlassian.net/browse/COMLAB-81)
- Release E1–E8: PR #121.

## 7. Límites conocidos

- La demostración pública usa el plan gratuito de Render.
- PostgreSQL Free debe recrearse o migrarse antes de su vencimiento.
- El adaptador OCI fue implementado y el bucket fue validado por separado; el despliegue Render actual usa el backend local configurado en el Blueprint y no debe confundirse con persistencia permanente de archivos.
- Las credenciales OCI permanecen fuera de Git.
