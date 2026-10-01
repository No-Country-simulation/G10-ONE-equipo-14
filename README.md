# CommunityLab

Proyecto del equipo **G10 · Hackaton ONE · Equipo 14**. Desafío: Motor Inteligente de
Transformación y Distribución para Comunidades Digitales.

## Introducción

CommunityLab transforma interacciones de comunidades digitales en oportunidades y borradores
de contenido. El MVP procesa archivos JSON o CSV, analiza sentimiento, temas y relevancia
mediante IA, genera contenido para LinkedIn y FAQ, permite revisión humana y almacena el
resultado final en OCI Object Storage.

## Objetivos

- Procesar y deduplicar interacciones de la comunidad.
- Detectar temas, sentimiento, relevancia y oportunidades de contenido.
- Generar borradores de LinkedIn y FAQ basados en evidencia.
- Permitir editar, aprobar o rechazar los activos generados.
- Mantener trazabilidad y guardar los paquetes aprobados en OCI.

## Arquitectura

Flujo principal:

```
JSON/CSV -> FastAPI -> Pydantic -> PostgreSQL -> LangGraph -> LLM Gateway
-> reglas de negocio -> Streamlit -> aprobación -> OCI Object Storage
```

Componentes principales:

- **FastAPI y Pydantic** — API, contratos y validación.
- **LangGraph y LLM Gateway** — análisis y generación estructurada con proveedor de IA intercambiable.
- **PostgreSQL** — estado, trazabilidad y auditoría.
- **Streamlit** — carga, visualización y curaduría humana.
- **OCI Object Storage** — almacenamiento de paquetes, manifiestos y activos aprobados.
- **Git y GitHub** — versionado del código: [G10-ONE-equipo-14](https://github.com/No-Country-simulation/G10-ONE-equipo-14).
- **Jira** — gestión del proyecto, backlog y tickets: [Proyecto CommunityLab en Jira](https://g10-latam-equipo14.atlassian.net/).

## Estructura del repositorio

```
app/         # API FastAPI, contratos, dominio, servicios y persistencia
alembic/     # Migraciones de PostgreSQL
dashboard/   # Interfaz Streamlit actual
data/        # Datos de demostración JSON y CSV
docs/        # Documentación técnica y de producto
tests/       # Pruebas unitarias, de contrato e integración
```

## Setup

1. Clonar el [repositorio](https://github.com/No-Country-simulation/G10-ONE-equipo-14).
2. Instalar Docker y Docker Compose.
3. Copiar `.env.example` como `.env` y ajustar la configuración local.
4. Ejecutar `docker compose up -d --build`. La API aplica las migraciones antes de iniciar.
5. Abrir Swagger en `http://localhost:8000/docs` y el dashboard en `http://localhost:8501`.
6. En el dashboard, cargar `data/sample_interactions.json` o `data/sample_interactions.csv` y verificar el resumen persistido.
7. Ejecutar `python -m pytest -q tests` dentro de un entorno con las dependencias instaladas.
8. Gestionar tareas, responsables y avances desde [Jira](https://g10-latam-equipo14.atlassian.net/).

## Estado actual

🚧 En construcción.

Implementado actualmente:

- API FastAPI v1, contratos Pydantic y health check de PostgreSQL.
- Ingesta JSON/CSV, normalización, deduplicación e idempotencia persistidas.
- Tablas `interactions` y `runs` con migraciones Alembic reproducibles.
- Dashboard técnico de estado y CI con PostgreSQL 16.

Pendiente para completar el MVP:

- Consulta persistida de ejecuciones mediante `GET /api/v1/runs/{run_id}`.
- Análisis y generación con LLM/LangGraph.
- Curaduría y aprobación de activos en Streamlit.
- Publicación de paquetes aprobados en OCI Object Storage.

## Convenciones de contribución

Branching, PRs y Definition of Done se documentan en [CONTRIBUTING.md](CONTRIBUTING.md) y [docs/GIT_WORKFLOW.md](docs/GIT_WORKFLOW.md).
