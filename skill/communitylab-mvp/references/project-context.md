# Contexto y fuentes de CommunityLab

Lee sólo las secciones y fuentes necesarias para la tarea. Este mapa evita mezclar el enunciado general del hackathon, el diseño elegido por el equipo y el estado real del repositorio.

## Prioridad de las fuentes

1. **Comportamiento implementado:** código, migraciones y pruebas actuales.
2. **Contrato vigente:** `app/schemas/v1/`, rutas de `app/api/v1/` y pruebas de contrato.
3. **MVP elegido por el equipo:** `docs/CommunityLab_MVP.pdf` y `README.md`.
4. **Reglas editoriales y de producto:** `docs/criterios_creacion_contenido.md`.
5. **Requisito externo original:** `docs/PROYECTO-communityLAB-Motot Inteligente de Transformación y Distribución para Comunidades Digitales.pdf`.
6. **Ejemplos no normativos:** `docs/ejemplo_datos_crudos_discord.json` y `docs/ejemplo_contenido_salida.md`.

Si dos fuentes difieren, no elijas una en silencio. Para implementar, conserva el contrato vigente salvo que la tarea pida migrarlo. Para evaluar cumplimiento del hackathon, compara el estado actual con el requisito externo y el MVP elegido.

## Alcance obligatorio del desafío

- Ingesta funcional de interacciones simuladas o reales.
- Análisis con LLM de sentimiento, temas y relevancia.
- Al menos dos formatos de activos de marketing o distribución.
- Orquestación con n8n, LangChain, LangGraph, Python o equivalente.
- Interfaz amigable de curaduría o aprobación.
- Integración con OCI Object Storage dentro de la capa gratuita indicada por el programa.
- Demostración de al menos tres transformaciones y documentación del pipeline.

El enunciado permite elegir tecnologías y formatos. No convierte todas sus sugerencias en requisitos simultáneos.

## Decisiones del MVP del equipo

- FastAPI y Pydantic v2 para API y contratos.
- PostgreSQL para estado, trazabilidad y auditoría.
- LangGraph y un gateway de LLM intercambiable para análisis y generación.
- Streamlit para carga, visualización, edición, aprobación y rechazo.
- OCI Object Storage para `raw`, `analyzed`, `generated`, `approved` y `manifests`.
- Docker Compose para ejecución local.
- Lotes JSON o CSV de hasta 500 interacciones.
- Dos activos: LinkedIn y FAQ.
- Curaduría humana obligatoria y ninguna publicación automática.

## Estado observado del repositorio al crear esta referencia

Consulta siempre los archivos actuales antes de confiar en este resumen.

- Están implementados los schemas v1, health check, ingesta JSON/CSV, normalización, fingerprint, persistencia de interacciones e idempotencia de ejecuciones.
- `POST /api/v1/process` y `POST /api/v1/process/csv` persisten la ingesta y devuelven `202`. Los campos de análisis, oportunidades, activos, aprobaciones y manifest todavía se devuelven vacíos o ausentes.
- Los endpoints de listado/edición/aprobación de activos y consulta de runs son scaffolding; varias operaciones responden `501`.
- LangGraph, el gateway de LLM, la generación real, el quality gate, la persistencia de activos/aprobaciones y el adaptador de OCI aún no aparecen implementados en el código revisado.
- `docs/INTERACTION_TABLE.md` conserva una nota antigua que llama mock al endpoint `/process`; confirma el comportamiento en el código y actualiza esa nota si una tarea toca esa documentación.
- El ejemplo de solicitud/respuesta del PDF original usa nombres en español que no corresponden al contrato v1 vigente.

## Rutas clave

- Contratos: `app/schemas/v1/`
- Endpoints: `app/api/v1/endpoints/`
- Ingesta e idempotencia: `app/services/`
- Fingerprint y reglas puras: `app/domain/`
- Modelos y migraciones: `app/db/models/` y `alembic/versions/`
- Dashboard: `dashboard/`
- Pruebas: `tests/`
- Datos de demostración: `data/` y `docs/ejemplo_datos_crudos_discord.json`

## Reglas editoriales relevantes

- Prioriza una alerta interna sobre cualquier oportunidad pública cuando exista frustración alta o riesgo para un miembro. Las alertas nunca son contenido público, aunque no sean uno de los dos activos del MVP.
- Una pregunta técnica no recurrente puede derivarse a mentoría sin generar FAQ.
- Los highlights son agregaciones por periodo y no deben producirse a partir de un archivo que no demuestre cobertura completa del periodo.
- No uses una referencia textual a preguntas anteriores como si fueran múltiples mensajes independientes. El umbral de recurrencia debe ser configurable y sustentado por los datos disponibles.
- No afirmes que un incidente fue resuelto si la evidencia sólo muestra que fue escalado o que se prometió seguimiento.
