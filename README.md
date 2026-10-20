# CommunityLab

Motor inteligente de transformación y distribución para comunidades digitales, desarrollado por **G10 · Hackathon ONE · Equipo 14**.

CommunityLab recibe interacciones en JSON o CSV, las normaliza, deduplica y guarda en PostgreSQL. El pipeline analiza las interacciones, detecta oportunidades, genera activos LinkedIn/FAQ y permite curarlos antes de su publicación mediante un adaptador de almacenamiento.

## Demo pública

- Aplicación: https://communitylab-dashboard.onrender.com
- API: https://communitylab-api.onrender.com
- Swagger/OpenAPI: https://communitylab-api.onrender.com/docs
- Health: https://communitylab-api.onrender.com/api/v1/health

El entorno está desplegado con el plan gratuito de Render y puede tardar cerca de un minuto en despertar después de un período sin actividad. La base gratuita de demostración expira a los 30 días.

## Estado del proyecto

### Implementado

- API REST con FastAPI y contratos versionados con Pydantic.
- Carga de interacciones JSON y CSV.
- Normalización, fingerprint SHA-256 y deduplicación por comunidad.
- Idempotencia persistida mediante el encabezado `Idempotency-Key`.
- Cola asíncrona durable en PostgreSQL y worker independiente para lotes grandes.
- PostgreSQL 16 con migraciones Alembic automáticas.
- Dashboard Streamlit para cargar archivos y visualizar el resultado.
- Health checks de PostgreSQL y API.
- Logs JSON para solicitudes, análisis/reintentos y almacenamiento, sin contenido sensible.
- Pipeline de análisis, detección de PII y oportunidades.
- Generación versionada de activos LinkedIn y FAQ.
- FAQ basada en recurrencia temática, con umbral configurable.
- Curaduría persistente: edición, aprobación y rechazo.
- Interfaz visual con identidad de CommunityLab, ayuda contextual y separación
  explícita entre controles editables e información de solo lectura.
- Adaptadores de almacenamiento local y OCI con manifiestos verificables.
- Suite de **159 pruebas aprobadas** y CI en GitHub Actions.
- Datos de demostración en JSON y CSV.

### Último cierre verificado

El 17 de octubre de 2026 se publicó en `main` la mejora visual y de ayuda del
dashboard mediante los PR [#220](https://github.com/No-Country-simulation/G10-ONE-equipo-14/pull/220)
y [#221](https://github.com/No-Country-simulation/G10-ONE-equipo-14/pull/221).
La ejecución de CI de producción
[#38999088448](https://github.com/No-Country-simulation/G10-ONE-equipo-14/actions/runs/38999088448)
aprobó calidad, Terraform, 159 pruebas y smoke tests públicos. La versión
desplegada se verificó además en navegador, con API y PostgreSQL operativos y
sin errores de consola.

### Trabajo deliberadamente pendiente

- Migrar o recrear PostgreSQL antes del vencimiento del plan gratuito de Render.
- Ejecutar INV-002 a INV-005 durante el despliegue final: activar OCI, completar
  layout y manifest, y mostrar el recibo de publicación en Streamlit.
- Configurar credenciales OCI únicamente en ese entorno; nunca en el repositorio.

Todos los puntos funcionales no OCI del inventario están completados. La
trazabilidad del cierre y los cuatro pendientes deliberados se detallan en
[`docs/INVENTARIO_PROYECTO.md`](docs/INVENTARIO_PROYECTO.md).

## Criterios de salida del MVP y Definición de Terminado (Done)

De acuerdo con la especificación fundacional del proyecto ([`docs/CommunityLab_MVP.pdf`](docs/CommunityLab_MVP.pdf), secciones 2 y 10), el plan por etapas ([`docs/ROADMAP_ETAPAS.md`](docs/ROADMAP_ETAPAS.md)) y el inventario técnico auditado ([`docs/INVENTARIO_PROYECTO.md`](docs/INVENTARIO_PROYECTO.md)), a continuación se formaliza el cumplimiento y verificación de todos los criterios de salida del MVP, criterios de éxito del negocio y la definición de terminado (Done).

### Matriz de criterios de salida por fase del MVP

| Fase | Entrega técnica | Criterio de salida oficial | Estado | Verificación y evidencia técnica |
|---|---|---|:---:|---|
| **1. Base** | Repositorio, Docker Compose, endpoint `/health`, contratos Pydantic v1 y datasets de muestra. | **Entorno reproducible** | Cumplido | `docker compose up -d --build` inicia de forma reproducible `db` (PostgreSQL 16), `api` (FastAPI), `dashboard` (Streamlit) y `worker`. Endpoint `GET /api/v1/health` verifica API y base de datos operativas. Contratos en `app/schemas/v1/`. |
| **2. Ingesta** | Endpoints JSON, CSV y webhook, fingerprint SHA-256, deduplicación e idempotencia en PostgreSQL. | **20 registros sin duplicados** | Cumplido | Datasets de 20+ interacciones en `data/sample_interactions.json` y `data/sample_interactions.csv`. Deduplicación estricta por `(community_id, fingerprint)` en tabla `interactions`. Idempotencia persistente vía header `Idempotency-Key` en tabla `runs`. Validado en `tests/test_ingestion.py` y `test_idempotency.py`. |
| **3. IA** | Gateway de LLM (Gemini / Mock determinístico), extracción estructurada, grounding y router determinístico. | **Salida estructurada estable** | Cumplido | `app/ai/gateway.py` soporta `gemini-3.1-flash-lite` y proveedor `mock` sin red. Extracción de sentimiento, tópicos, relevancia, confianza y evidencia textual directa. Calidad: 100% validez de esquema y 100% grounding (`docs/evidence/INV-024-quality-evaluation/README.md`). Detección y redacción de PII (`tests/test_pii_detection.py`). |
| **4. Contenido** | Generadores especializados para LinkedIn y FAQ con fuentes y evidencia vinculada. | **Dos activos con evidencia** | Cumplido | `app/services/content_generation.py`: generación de post para LinkedIn ante logros/testimonios (relevancia >= 0.75) y preguntas frecuentes (FAQ) agrupadas por recurrencia temática (`FAQ_RECURRENCE_THRESHOLD >= 2`). Cada activo preserva `source_interaction_ids` y extractos de respaldo. Validado en `tests/test_content_generation.py` y `test_faq_recurrence.py`. |
| **5. Curaduría** | Dashboard Streamlit con cola persistente, edición versionada, aprobación, rechazo y auditoría. | **Editar, aprobar y rechazar** | Cumplido | Cola viva consultando `GET /api/v1/assets?status=PENDING_REVIEW`. Máquina de estados explícita (`DRAFT` -> `PENDING_REVIEW` -> `APPROVED` \| `REJECTED`). Edición incrementa versión (`asset_versions`) y reabre a revisión; aprobación inmutable con registro de revisor y timestamp. Validado en `tests/test_asset_curation.py`. |
| **6. Almacenamiento / OCI** | Adaptador de almacenamiento desacoplado, paquete JSON, manifest con SHA-256 y publicación idempotente. | **Objeto verificable en bucket** | Cumplido (Alcance funcional) | `app/services/object_storage.py`: implementación de `StorageAdapter` desacoplado (backend local y cliente OCI). Genera paquete con checksum SHA-256 de 64 caracteres, ETag, fecha y `manifest.json`. Publicación idempotente con recibo verificable (`tests/test_object_storage.py`). Activación del bucket productivo planificada sin secretos en repo (INV-002–INV-005 en `docs/INVENTARIO_PROYECTO.md`). |
| **7. Cierre** | Suite automatizada completa, documentación operativa, guías funcionales y recorridos punta a punta. | **Tres recorridos reproducibles** | Cumplido | Suite de **159 pruebas aprobadas** (unitarias, integración, contrato y E2E en `tests/test_e2e_mvp.py`). CI en GitHub Actions verde. Guía funcional paso a paso en `docs/sets_pruebas/GUIA_PRUEBA_FUNCIONAL.md` y guion en `docs/DEMO_GUIDE.md`. |

### Criterios de éxito del MVP

Conforme a la sección 2 de [`docs/CommunityLab_MVP.pdf`](docs/CommunityLab_MVP.pdf), el sistema cumple todos los criterios de éxito cuantitativos y operativos:

1. **Procesar al menos 20 interacciones de prueba y mostrar errores por registro:** Cumplido con `data/sample_interactions.json` y `data/sample_interactions.csv`, informando cantidad de recibidas, aceptadas, duplicadas y errores específicos por fila.
2. **Obtener sentimiento, temas, relevancia, confianza y evidencia para cada interacción:** Cumplido y persistido en la tabla `analyses`, visible en la pestaña de análisis del dashboard y en `GET /api/v1/runs/{run_id}`.
3. **Detectar al menos tres oportunidades y generar dos tipos de activos:** Cumplido; el motor detecta oportunidades priorizadas y genera activos versionados para canales `LINKEDIN` y `FAQ`.
4. **Editar, aprobar o rechazar activos desde Streamlit:** Cumplido mediante interfaz de curaduría persistente con feedback inmediato y prevención de errores.
5. **Guardar el paquete aprobado y su manifest con SHA-256:** Cumplido; la publicación genera el recibo con `object_key`, `bucket`, `etag` y hash inmutable SHA-256.
6. **Demostrar tres transformaciones completas y reproducibles:** Cumplido en la suite automatizada (`tests/test_e2e_mvp.py`) y reproducible interactivamente desde el dashboard.

### Los tres recorridos demostrables obligatorios

Los tres recorridos requeridos para el cierre del MVP están automatizados en `tests/test_e2e_mvp.py` y documentados paso a paso en [`docs/DEMO_GUIDE.md`](docs/DEMO_GUIDE.md) y [`docs/sets_pruebas/GUIA_PRUEBA_FUNCIONAL.md`](docs/sets_pruebas/GUIA_PRUEBA_FUNCIONAL.md):

1. **Recorrido 1 — Logro a post de LinkedIn aprobado y publicado:**
   - **Entrada:** Interacción con testimonio o logro técnico (ej. *"Gracias, conseguí entregar FastAPI con PostgreSQL y Docker"*).
   - **Procesamiento:** Se clasifica con relevancia >= 0.75, genera una oportunidad de tipo contenido y un activo borrador para `LINKEDIN`.
   - **Curaduría:** El curador inspecciona el borrador, revisa las fuentes textuales vinculadas, lo aprueba (`POST /api/v1/assets/{id}/approve`) y lo publica (`POST /api/v1/assets/{id}/publish`), obteniendo el manifest con checksum SHA-256.
2. **Recorrido 2 — Pregunta técnica recurrente a FAQ aprobada:**
   - **Entrada:** Interacciones de tipo `question` que superan el umbral de recurrencia (`FAQ_RECURRENCE_THRESHOLD >= 2`) sobre la misma temática (ej. configuración de Docker y PostgreSQL).
   - **Procesamiento:** El router agrupa las preguntas afines y genera un activo consolidado para `FAQ` formulado en formato de pregunta (`?`) con respuesta fundamentada.
   - **Curaduría:** El curador edita el texto para ajustar tono o contenido (creando una nueva versión de activo) y lo aprueba (`APPROVED`).
3. **Recorrido 3 — Contenido sensible o frustración bloqueado (Sin activos públicos):**
   - **Entrada:** Interacción que contiene datos personales directos (correo electrónico, teléfono) o sentimiento de frustración/queja severa.
   - **Procesamiento:** La detección de PII anonimiza los datos sensibles (`[EMAIL]`, `[PHONE]`, `[PERSON]`). El router clasifica la oportunidad en estado `BLOCKED` y abre una alerta interna en `GET /api/v1/alerts`.
   - **Resultado:** No se genera ningún activo público ni se envía a la cola de curaduría de LinkedIn/FAQ, salvaguardando la privacidad de los usuarios y la reputación de la comunidad.

### Definición de terminado (Definition of Done - DoD)

| Criterio DoD | Evidencia de cumplimiento |
|---|---|
| **Pruebas y calidad de código** | **159 pruebas aprobadas** en PostgreSQL aislado (`tests/`). Linter `ruff check` aprobado sin advertencias. Dependencias auditadas con `pip-audit`. |
| **Seguridad y secretos** | Cero secretos, tokens o claves en el repositorio. `.gitignore` y `.dockerignore` estrictos. `.env.example` sanitizado. Variables privadas inyectadas exclusivamente en runtime. |
| **Versionado formal** | Contratos Pydantic versionados en `app/schemas/v1/`. Prompts versionados en `app/services/content_generation.py`. Modelos de BD gestionados con migraciones Alembic bidireccionales (`upgrade`/`downgrade`). |
| **Reproducibilidad y despliegue** | Ejecución local en un comando con `docker compose up -d --build`. Entorno público desplegado en Render con HTTPS, health check y smoke tests automatizados en CI. |
| **Casos feliz y de error documentados** | Manejo documentado de duplicados por fingerprint, rechazo de lotes inválidos, timeouts de red y fallbacks de IA en [`docs/MANUAL_USUARIO.md`](docs/MANUAL_USUARIO.md) y [`docs/sets_pruebas/GUIA_PRUEBA_FUNCIONAL.md`](docs/sets_pruebas/GUIA_PRUEBA_FUNCIONAL.md). |
| **Trazabilidad y auditoría** | Identificadores persistidos `run_id`, `interaction_id`, `source_ids`, `model_version`, `prompt_version`, usuario revisor y timestamps en PostgreSQL. |

## Especificación de requerimientos del sistema

El diseño e implementación de CommunityLab responden a los requisitos del Hackathon ONE G10 y a las especificaciones técnicas auditadas en [`docs/CommunityLab_MVP.pdf`](docs/CommunityLab_MVP.pdf) e [`docs/INVENTARIO_PROYECTO.md`](docs/INVENTARIO_PROYECTO.md).

### Requerimientos funcionales (RF)

| ID | Módulo / Área | Requerimiento funcional | Criterio de aceptación / Validación | Componente / Implementación | Estado |
|---|---|---|---|---|:---:|
| **RF-01** | Ingesta | Ingesta de archivos en formato JSON con validación de contrato. | Procesa payloads JSON según schema versionado `v1`, validando tipos y campos obligatorios. | `app/api/v1/endpoints/process.py` (`POST /process`) | Cumplido |
| **RF-02** | Ingesta | Ingesta de archivos CSV con soporte de alias y múltiples codificaciones. | Acepta cabeceras canónicas (`author`, `channel`, `type`, `text`) y alias en UTF-8 y Windows-1252. | `app/api/v1/endpoints/process.py` (`POST /process/csv`) | Cumplido |
| **RF-03** | Ingesta | Ingesta unitaria y automática en tiempo real vía Webhook. | Endpoint neutral protegido para eventos de Discord, Slack o n8n con clave idempotente `source + event_id`. | `app/api/v1/endpoints/webhooks.py` | Cumplido |
| **RF-04** | Ingesta | Reporte granular de errores por registro en cargas CSV. | Informa filas erróneas de forma aislada sin abortar el procesamiento de las filas válidas del lote. | `app/services/csv_ingestion.py` | Cumplido |
| **RF-05** | Deduplicación | Deduplicación por contenido mediante Fingerprint SHA-256. | Normaliza texto (minúsculas, espacios, puntuación) y genera hash SHA-256 único por comunidad en BD. | `app/domain/fingerprint.py`, tabla `interactions` | Cumplido |
| **RF-06** | Idempotencia | Idempotencia persistente en todas las solicitudes de procesamiento. | Exige header `Idempotency-Key`. Reintentos devuelven el mismo `run_id`; cambio de payload retorna HTTP 409. | `app/services/idempotency.py`, tabla `runs` | Cumplido |
| **RF-07** | Persistencia | Almacenamiento relacional de ejecuciones e interacciones normalizadas. | Persistencia en PostgreSQL 16 con claves foráneas, restricciones de unicidad e índices optimizados. | `app/db/models/`, `alembic/versions/` | Cumplido |
| **RF-08** | Privacidad | Detección y redacción automática de datos personales (PII). | Correos y teléfonos se reemplazan por `[EMAIL]` y `[PHONE]` antes de persistir o invocar IA. | `app/services/pii_detection.py` | Cumplido |
| **RF-09** | Privacidad | Gestión de consentimiento y directiva de exclusión (`opt_out`). | Sin consentimiento (`publication_consent: false`), autor se anonimiza como `[PERSON]`; con `opt_out: true` no genera activos. | `app/services/normalization.py` | Cumplido |
| **RF-10** | Pipeline IA | Gateway desacoplado para modelos LLM con proveedor intercambiable. | Soporta Google Gemini (`gemini-3.1-flash-lite`) para producción y Mock determinístico para testing y CI. | `app/ai/gateway.py`, `gemini_provider.py` | Cumplido |
| **RF-11** | Pipeline IA | Extracción analítica estructurada con Grounding verificable. | Extrae sentimiento, temas, entidades, relevancia (0-1), confianza (0-1) y citas textuales exactas (`evidence`). | `app/ai/gateway.py`, tabla `analyses` | Cumplido |
| **RF-12** | Pipeline IA | Resiliencia con reintento correctivo y fallback controlado. | Corrige respuestas de modelo mal formateadas; permite fallback a `mock` sólo si está configurado explícitamente. | `app/services/resilient_analysis.py` | Cumplido |
| **RF-13** | Decisión | Router determinístico de oportunidades basado en reglas de negocio. | Clasifica oportunidades en Python según sentimiento, relevancia y tipo sin delegar decisiones críticas al prompt. | `app/services/opportunity_detection.py` | Cumplido |
| **RF-14** | Decisión | Detección y escalamiento de Alertas Internas de máxima prioridad. | Sentimiento negativo/frustración crea alerta `OPEN` en BD, bloquea oportunidad pública y no genera activos. | `app/api/v1/endpoints/alerts.py` | Cumplido |
| **RF-15** | Contenido | Generación de FAQ por recurrencia temática configurable. | Agrupa preguntas afines y genera activo FAQ sólo si el grupo alcanza o supera `FAQ_RECURRENCE_THRESHOLD` (2). | `app/services/faq_recurrence.py` | Cumplido |
| **RF-16** | Contenido | Generador de publicaciones inspiradoras para LinkedIn con citas. | Genera posts estilo storytelling ante testimonios/logros (relevancia >= 0.75) con extractos y hashtags. | `app/services/content_generation.py` | Cumplido |
| **RF-17** | Contenido | Generador de preguntas frecuentes estructuradas con formato canónico. | Redacta la pregunta en tono didáctico finalizada en `?` con respuesta fundamentada en los `source_ids`. | `app/services/content_generation.py` | Cumplido |
| **RF-18** | Curaduría | Cola viva y persistente de curaduría en Streamlit. | Consulta `GET /api/v1/assets?status=PENDING_REVIEW` conectada a PostgreSQL con botón de refresco manual. | `dashboard/app.py`, `api_client.py` | Cumplido |
| **RF-19** | Curaduría | Máquina de estados explícita e inmutable para activos. | Estados: `DRAFT` → `PENDING_REVIEW` → `APPROVED` o `REJECTED`. Activos aprobados son inmutables. | `app/api/v1/endpoints/assets.py` | Cumplido |
| **RF-20** | Curaduría | Edición de borradores con versionado histórico auditable. | Modificar un borrador genera una nueva fila en `asset_versions` con versión incremental (v1, v2...). | `app/db/models/asset_version.py` | Cumplido |
| **RF-21** | Curaduría | Auditoría persistente de decisiones humanas de curaduría. | Registra en tabla `approvals` el revisor, timestamp de auditoría, decisión y comentarios asociados. | `app/db/models/approval.py` | Cumplido |
| **RF-22** | Almacenamiento | Adaptador de almacenamiento desacoplado (Local / OCI Object Storage). | Interfaz `StorageAdapter` con backends intercambiables para disco local y Oracle Cloud Infrastructure. | `app/services/object_storage.py` | Cumplido |
| **RF-23** | Almacenamiento | Generación de Manifiesto inmutable con checksums SHA-256 y ETag. | Crea `manifest.json` con metadatos del paquete, lista de archivos, tipos MIME, hash de 64 caracteres y fecha. | `app/services/object_storage.py` | Cumplido |
| **RF-24** | Almacenamiento | Publicación idempotente con emisión de recibo verificable. | Publicar un activo aprobado genera recibo con `bucket`, `object_key`, `etag` y `sha256`, evitando duplicados. | `POST /api/v1/assets/{id}/publish` | Cumplido |
| **RF-25** | Consultabilidad | Consulta histórica completa de ejecuciones por `run_id`. | Recupera en cualquier momento el resumen, análisis, oportunidades y activos generados por un UUID de ejecución. | `GET /api/v1/runs/{run_id}` | Cumplido |
| **RF-26** | Asíncrono | Encolado asíncrono durable de lotes masivos de interacciones. | `POST /api/v1/process/async` responde de inmediato con `job_id` y delega la ejecución al worker. | `app/api/v1/endpoints/process.py` | Cumplido |
| **RF-27** | Asíncrono | Monitoreo y consulta de estado de procesamiento por lotes. | Expone `GET /api/v1/jobs/{job_id}` para consultar transición de estados: `PENDING` → `RUNNING` → `SUCCEEDED` / `FAILED`. | `app/api/v1/endpoints/jobs.py` | Cumplido |

---

### Requerimientos no funcionales (RNF)

| ID | Categoría (ISO 25010) | Requerimiento no funcional | Métrica / Verificación técnica | Estado |
|---|---|---|---|:---:|
| **RNF-01** | Rendimiento | Tiempo de procesamiento síncrono para lotes estándar. | Procesamiento completo de 20 interacciones en < 30 segundos usando proveedor LLM. | Cumplido |
| **RNF-02** | Rendimiento | Capacidad y latencia para procesamiento masivo asíncrono. | Encolado de 500 registros en < 1 s (0.062 s medido) y procesamiento por worker en < 30 s (19.84 s medido). | Cumplido |
| **RNF-03** | Concurrencia | Ejecución de workers segura y libre de condiciones de carrera. | Uso de bloqueo a nivel de fila `SELECT ... FOR UPDATE SKIP LOCKED` en PostgreSQL para orquestar workers concurrentes. | Cumplido |
| **RNF-04** | Seguridad | Política estricta de Cero Secretos en el repositorio. | `.gitignore` y `.dockerignore` validados; secretos inyectados exclusivamente vía variables de entorno en runtime. | Cumplido |
| **RNF-05** | Seguridad | Protección y control de acceso en operaciones de mutación. | Endpoints de escritura controlados por `MUTATIONS_ENABLED`, validación opcional de `X-API-Key` y rate limit por IP. | Cumplido |
| **RNF-06** | Seguridad | Configuración y restricción de orígenes cruzados (CORS). | Acceso limitado exclusivamente a los dominios configurados en `CORS_ORIGINS` (dashboard local y producción). | Cumplido |
| **RNF-07** | Privacidad | Observabilidad y logs estructurados sin fuga de datos sensibles. | Logs en formato JSON estructurado con métricas de duración, estado y códigos HTTP, sin incluir textos ni PII. | Cumplido |
| **RNF-08** | Fiabilidad | Consistencia e idempotencia persistente ante fallos de red. | Toda operación de escritura es idempotente con claves persistidas en PostgreSQL que resisten reinicios de servicios. | Cumplido |
| **RNF-09** | Disponibilidad | Verificación de salud activa en todos los componentes. | Health checks automáticos en Docker y endpoint `GET /api/v1/health` validando conectividad a base de datos. | Cumplido |
| **RNF-10** | Mantenibilidad | Cobertura y reproducibilidad de pruebas automatizadas. | Suite de **159 pruebas automatizadas** (unitarias, integración, contrato y E2E) ejecutables en un entorno aislado. | Cumplido |
| **RNF-11** | Calidad de código | Cumplimiento de estándares de estilo, análisis estático y seguridad. | Linter `ruff check` aprobado sin advertencias y análisis de dependencias sin vulnerabilidades vía `pip-audit`. | Cumplido |
| **RNF-12** | Portabilidad | Despliegue estandarizado y reproducible con contenedores. | Orquestación mediante Docker y Docker Compose v2 levantando API, Dashboard, Base de datos y Worker. | Cumplido |
| **RNF-13** | Operabilidad | Respaldo y restauración comprobables sin riesgo de pérdida. | Scripts `deploy/backup.sh` y `verify-backup.sh` con verificación de catálogo, restauración en BD aislada y retención de 7 días. | Cumplido |
| **RNF-14** | Integridad | Verificabilidad criptográfica de contenido almacenado. | Todo paquete publicado genera un hash inmutable SHA-256 de 64 caracteres y un ETag persistido en `manifest.json`. | Cumplido |
| **RNF-15** | Usabilidad | Experiencia de usuario contextual con manejo seguro de errores. | Dashboard Streamlit con identidad propia, ayuda integrada, separación de campos editables y captura de errores sin crasheo. | Cumplido |

---

## Arquitectura y flujos de procesos (Mermaid)

### 1. Diagrama de arquitectura general y pipeline E2E

```mermaid
flowchart TD
    subgraph Fuentes ["1. Fuentes de Entrada"]
        JSON["Archivo JSON"]
        CSV["Archivo CSV"]
        WH["Webhook (Discord / Slack / n8n)"]
    end

    subgraph Ingesta ["2. Ingesta, Deduplicación e Idempotencia"]
        API["FastAPI (Contratos Pydantic v1)"]
        Fing["Normalizador y Fingerprint SHA-256"]
        Idemp{"¿Idempotency-Key registrada?"}
        DB_Runs[("PostgreSQL: Tabla runs")]
        DB_Inter[("PostgreSQL: Tabla interactions")]
    end

    subgraph Pipeline ["3. Pipeline de IA y Decisión"]
        PII["Filtro de Privacidad (Redacción PII)"]
        Gateway["Gateway LLM (Gemini 3.1 / Mock)"]
        QualityGate["Quality Gate (Validez y Grounding)"]
        Router{"Router Determinístico"}
        Alerts[("PostgreSQL: Alertas Internas")]
    end

    subgraph Generacion ["4. Generación de Activos"]
        GenLinkedIn["Generador LinkedIn (Logros >= 0.75)"]
        GenFAQ["Generador FAQ (Recurrencia >= 2)"]
    end

    subgraph Curaduria ["5. Curaduría Humana (Streamlit)"]
        Queue["Cola PENDING_REVIEW"]
        Decision{"Decisión Humana"}
        Edit["Editar (Nueva Versión vN+1)"]
        Approve["Aprobar (APPROVED)"]
        Reject["Rechazar (REJECTED)"]
    end

    subgraph Storage ["6. Almacenamiento y Manifiesto"]
        Adapter["StorageAdapter (Local / OCI)"]
        Pkg["Paquete JSON + Hash SHA-256 + ETag"]
        Manifest[("PostgreSQL: manifests / manifest.json")]
    end

    JSON --> API
    CSV --> API
    WH --> API
    API --> Idemp
    Idemp -->|Registrada| DB_Runs
    Idemp -->|Nueva| Fing
    Fing --> DB_Inter
    DB_Inter --> PII
    PII --> Gateway
    Gateway --> QualityGate
    QualityGate --> Router
    Router -->|Frustración / PII sensible| Alerts
    Router -->|Testimonio / Logro| GenLinkedIn
    Router -->|Duda técnica recurrente| GenFAQ
    GenLinkedIn --> Queue
    GenFAQ --> Queue
    Queue --> Decision
    Decision -->|Ajustar texto| Edit
    Edit --> Queue
    Decision -->|Descartar| Reject
    Decision -->|Aprobar| Approve
    Approve --> Adapter
    Adapter --> Pkg
    Pkg --> Manifest
```

---

### 2. Flujo de ingesta, normalización, deduplicación e idempotencia

```mermaid
flowchart TD
    Req["Petición HTTP (POST /process o /process/csv)"] --> CheckHeader{"¿Header Idempotency-Key presente?"}
    CheckHeader -->|No| Err400["Error 400: Header obligatorio requerido"]
    CheckHeader -->|Sí| CheckRun{"¿Existe en tabla runs por comunidad?"}
    CheckRun -->|Mismo hash de solicitud| RetRun["Retornar respuesta previa (Idempotente)"]
    CheckRun -->|Distinto payload| Err409["Conflicto 409: Clave reutilizada con distinto contenido"]
    CheckRun -->|No existe| CreateRun["Crear registro en runs (Estado: PROCESSING)"]
    CreateRun --> ParseInput["Parsear elementos (JSON o CSV)"]
    ParseInput --> NormLoop["Normalizar: Limpieza de texto, fechas y metadatos"]
    NormLoop --> CalcHash["Calcular Fingerprint SHA-256 por interacción"]
    CalcHash --> DeduplCheck{"¿Existe fingerprint en la comunidad?"}
    DeduplCheck -->|Sí| MarkDup["Contabilizar como duplicada (No insertar)"]
    DeduplCheck -->|No| InsertInter["Insertar en tabla interactions"]
    MarkDup --> Summary["Consolidar resumen: recibidas, aceptadas, duplicadas, errores"]
    InsertInter --> Summary
    Summary --> UpdateRun["Actualizar estado del Run a COMPLETED"]
```

---

### 3. Flujo del pipeline de IA, privacidad y quality gate

```mermaid
flowchart TD
    Interactions["Interacciones Aceptadas"] --> CheckConsent{"¿publication_consent y opt_out?"}
    CheckConsent -->|opt_out = true| FlagNoPublish["Registrar trazabilidad: Bloquear activos públicos"]
    CheckConsent -->|consent = false| AnonAuthor["Anonimizar autor como [PERSON]"]
    CheckConsent -->|consent = true| KeepAuthor["Conservar autor original"]
    AnonAuthor --> RedactPII["Detección PII: Regex de correos y teléfonos"]
    KeepAuthor --> RedactPII
    FlagNoPublish --> RedactPII
    RedactPII --> SubstitutePII["Sustituir por [EMAIL] y [PHONE]"]
    SubstitutePII --> Gateway["LLM Gateway"]
    Gateway --> CallProvider{"ANALYSIS_PROVIDER"}
    CallProvider -->|gemini| GeminiAPI["API Google Gemini (gemini-3.1-flash-lite)"]
    CallProvider -->|mock| MockEngine["Motor Mock determinístico sin red"]
    GeminiAPI --> ValidateSchema{"Validación Schema Pydantic"}
    MockEngine --> ValidateSchema
    ValidateSchema -->|Falla formato| RetryFallback{"¿Reintento o Fallback mock habilitado?"}
    RetryFallback -->|Reintento correctivo| GeminiAPI
    RetryFallback -->|Fallback activo| MockEngine
    ValidateSchema -->|Válido| QualityGate["Quality Gate de Grounding"]
    QualityGate --> VerifyCitations["Verificar que las afirmaciones tengan citas textuales válidas"]
    VerifyCitations --> PersistAnalysis["Persistir en tabla analyses con model y prompt_version"]
```

---

### 4. Flujo del router determinístico y generación de activos

```mermaid
flowchart TD
    Analysis["Análisis Persistido (Sentimiento, Temas, Relevancia, Confianza)"] --> EvalPriority{"Evaluación de Reglas de Decisión"}
    
    EvalPriority -->|Sentimiento Negativo / Frustración| CaseAlert["Alerta Interna de Máxima Prioridad"]
    CaseAlert --> OpenAlert["Crear alerta OPEN en tabla alerts"]
    CaseAlert --> BlockOpp["Crear oportunidad con estado BLOCKED"]
    
    EvalPriority -->|Testimonio / Logro con Relevancia >= 0.75| CaseLinkedIn["Oportunidad de Contenido: Caso de Éxito"]
    CaseLinkedIn --> CreateOppLI["Registrar ContentOpportunity en BD"]
    CreateOppLI --> ExecPromptLI["Ejecutar LinkedInGenerator con prompt versionado"]
    ExecPromptLI --> AssetLI["Generar GeneratedAsset canal LINKEDIN (Status: PENDING_REVIEW)"]
    
    EvalPriority -->|Interacciones de tipo 'question'| CaseFAQ["Agrupador Temático de Dudas"]
    CaseFAQ --> CountRecurrence{"¿Recurrencia temática >= FAQ_RECURRENCE_THRESHOLD (2)?"}
    CountRecurrence -->|No (< 2)| SkipFAQ["Pregunta aislada: No genera activo (Derivar a mentoría)"]
    CountRecurrence -->|Sí (>= 2)| CreateOppFAQ["Registrar ContentOpportunity de FAQ"]
    CreateOppFAQ --> ExecPromptFAQ["Ejecutar FAQGenerator con citas de todas las preguntas"]
    ExecPromptFAQ --> AssetFAQ["Generar GeneratedAsset canal FAQ (Status: PENDING_REVIEW)"]
    
    EvalPriority -->|Mensaje neutro sin logro ni pregunta| SkipGeneral["No genera activo publicable"]
```

---

### 5. Máquina de estados y ciclo de vida de curaduría humana

```mermaid
stateDiagram-v2
    [*] --> DRAFT: Generado por motor de IA
    DRAFT --> PENDING_REVIEW: Ingreso a cola de curaduría en PostgreSQL
    
    state PENDING_REVIEW {
        [*] --> Inspeccionar: Lectura de título, cuerpo y fuentes vinculadas
        Inspeccionar --> ValidarPrivacidad: Confirmar anonimización y ausencia de PII
        ValidarPrivacidad --> Decidir
    }
    
    PENDING_REVIEW --> APPROVED: POST /assets/{id}/approve (Aprobar con revisor y timestamp)
    PENDING_REVIEW --> REJECTED: POST /assets/{id}/reject (Rechazar con revisor)
    PENDING_REVIEW --> PENDING_REVIEW: PATCH /assets/{id} (Editar: genera versión N+1)
    
    REJECTED --> PENDING_REVIEW: PATCH /assets/{id} (Reedición crea nueva versión pendiente)
    
    state APPROVED {
        [*] --> Inmutable: Registro protegido contra modificaciones
        Inmutable --> ListoPublicar: Habilitado para empaquetado y almacenamiento
    }
    
    APPROVED --> PUBLISHED: POST /assets/{id}/publish (Idempotente)
    PUBLISHED --> [*]: Manifiesto SHA-256 y recibo de publicación emitidos
```

---

### 6. Flujo de publicación, manifest y almacenamiento

```mermaid
flowchart TD
    ReqPub["Solicitud POST /api/v1/assets/{asset_id}/publish"] --> CheckAppr{"¿Estado del activo == APPROVED?"}
    CheckAppr -->|No| Err400["Error 400: Sólo activos aprobados son publicables"]
    CheckAppr -->|Sí| CheckExist{"¿Ya posee manifiesto registrado en PostgreSQL?"}
    CheckExist -->|Sí| RetExisting["Retornar recibo existente (Publicación idempotente)"]
    CheckExist -->|No| LockAsset["Bloqueo atómico de la fila del activo"]
    LockAsset --> BuildPackage["Construir paquete JSON con versión actual y metadatos"]
    BuildPackage --> CalcChecksums["Calcular checksum inmutable SHA-256 (64 hex) y ETag"]
    CalcChecksums --> AdaptStore{"STORAGE_BACKEND"}
    AdaptStore -->|local| LocalStore["Guardar en disco local: var/storage/approved/"]
    AdaptStore -->|oci| OCIStore["Subir objeto a Oracle Cloud Object Storage"]
    LocalStore --> BuildManifest["Generar manifest.json con schema_version, run_id y hashes"]
    OCIStore --> BuildManifest
    BuildManifest --> SaveManifestDB["Persistir registro en tabla manifests"]
    SaveManifestDB --> ReturnReceipt["Retornar recibo: bucket, object_key, etag, sha256"]
```

---

### 7. Flujo de procesamiento asíncrono para lotes masivos (Worker)

```mermaid
sequenceDiagram
    autonumber
    actor Cliente as "Cliente / Dashboard"
    participant API as "FastAPI (/api/v1)"
    participant DB as "PostgreSQL (jobs & runs)"
    participant Worker as "Background Worker"

    Cliente->>API: POST /api/v1/process/async (con Idempotency-Key)
    API->>DB: Crear registro de Job (Estado: PENDING, Payload)
    API-->>Cliente: HTTP 202 Accepted { job_id, status_url }
    
    loop Polling continuo del Worker
        Worker->>DB: SELECT * FROM jobs WHERE status = 'PENDING' FOR UPDATE SKIP LOCKED LIMIT 1
        DB-->>Worker: Retorna Job bloqueado exclusivamente
    end
    
    Worker->>DB: Actualizar Job a estado RUNNING
    Worker->>Worker: Ejecutar Pipeline E2E (Normalización, IA, Activos)
    
    alt Procesamiento Exitoso
        Worker->>DB: Persistir resultados y actualizar Job a SUCCEEDED
    else Error Inesperado
        Worker->>DB: Registrar error y actualizar Job a FAILED
    end
    
    loop Consulta de Estado del Cliente
        Cliente->>API: GET /api/v1/jobs/{job_id}
        API->>DB: Consultar registro del Job
        DB-->>API: Retornar estado actual
        API-->>Cliente: Estado (PENDING, RUNNING o SUCCEEDED con run_id)
    end
```

---

### 8. Flujos de interacción por rol de usuario (User Journeys)

#### 8.1 User Journey: Community Manager

```mermaid
flowchart TD
    CM(["Community Manager"]) --> CM1["1. Abrir Dashboard Streamlit (http://localhost:8501)"]
    CM1 --> CM2["2. Completar campos contextuales: Organización, Comunidad y Período"]
    CM2 --> CM3["3. Seleccionar archivo de interacciones (JSON o CSV)"]
    CM3 --> CM4["4. Presionar 'Procesar archivo'"]
    CM4 --> CM5["5. Inspeccionar Resumen: Total procesadas, aceptadas, duplicadas y errores"]
    CM5 --> CM6["6. Analizar métricas de comunidad: Sentimiento predominante y Temas top"]
    CM6 --> CM7["7. Acceder a pestaña 'Alertas Internas' para atender fricciones o reclamos"]
    CM7 --> CM8["8. Copiar Run ID para seguimiento o consultar ejecuciones anteriores"]
```

#### 8.2 User Journey: Curador de Contenido

```mermaid
flowchart TD
    Curator(["Curador de Contenido"]) --> CU1["1. Ingresar a pestaña 'LinkedIn y FAQ' en Dashboard"]
    CU1 --> CU2["2. Presionar 'Actualizar cola' para consultar activos PENDING_REVIEW"]
    CU2 --> CU3["3. Seleccionar activo y examinar propuesta de texto generada"]
    CU3 --> CU4["4. Inspeccionar sección 'Evidencia y fuentes' vinculada al activo"]
    CU4 --> CU5["5. Verificar cumplimiento de privacidad: autor anonimizado y 0 datos sensibles"]
    CU5 --> Decision{"Evaluación de Calidad Editorial"}
    Decision -->|Requiere mejoras de copy| CU6["Editar título o cuerpo en el formulario y 'Guardar edición'"]
    CU6 --> CU7["Sistema genera versión N+1 y mantiene activo en PENDING_REVIEW"]
    CU7 --> CU2
    Decision -->|Contenido no apropiado| CU8["Presionar 'Rechazar' (Activo pasa a REJECTED)"]
    Decision -->|Contenido excelente| CU9["Presionar 'Aprobar' (Activo pasa a APPROVED inmutable)"]
    CU9 --> CU10["Disparar publicación hacia Storage (Generación de paquete y manifest)"]
```

#### 8.3 User Journey: Equipo de Marketing y Difusión

```mermaid
flowchart TD
    Mkt(["Equipo de Marketing / Difusión"]) --> MK1["1. Consultar activos aprobados mediante API (GET /assets?status=APPROVED)"]
    MK1 --> MK2["2. Recuperar paquete JSON publicado con checksum SHA-256 verificado"]
    MK2 --> ChannelChoice{"Canal de Distribución"}
    ChannelChoice -->|Canal LinkedIn| MK3["Publicar borrador aprobado con storytelling y hashtags"]
    ChannelChoice -->|Canal FAQ / Docs| MK4["Integrar pregunta canónica y respuesta a la Base de Conocimiento"]
    MK3 --> MK5["3. Monitorear engagement y feedback de la comunidad"]
    MK4 --> MK5
```

---

## Servicios Docker

| Servicio | Tecnología | Dirección local | Responsabilidad |
| --- | --- | --- | --- |
| `db` | PostgreSQL 16 | red interna de Docker | Interacciones, ejecuciones e idempotencia |
| `api` | FastAPI | `http://localhost:8000` | Contratos, ingesta y persistencia |
| `dashboard` | Streamlit | `http://localhost:8501` | Demostración visual y carga de archivos |
| `worker` | Python/FastAPI services | red interna de Docker | Procesamiento asíncrono durable de lotes |

## Estructura del repositorio

```text
.
├── alembic/                 # Configuración y migraciones de PostgreSQL
│   └── versions/
├── app/
│   ├── api/v1/endpoints/    # Rutas FastAPI
│   ├── core/                # Configuración de la aplicación
│   ├── db/models/           # Modelos SQLAlchemy
│   ├── domain/              # Reglas de dominio y fingerprint
│   ├── schemas/v1/          # Contratos Pydantic versionados
│   └── services/            # Ingesta, CSV, normalización e idempotencia
├── dashboard/               # Frontend Streamlit y su Dockerfile
├── data/                    # Archivos JSON/CSV de demostración
├── docs/                    # Documentación funcional y técnica
├── tests/                   # Pruebas unitarias, contrato e integración
├── .env.example             # Variables locales de ejemplo
├── docker-compose.yml       # Orquestación local
├── Dockerfile               # Imagen de la API
└── requirements.txt         # Dependencias del backend
```

## Requisitos

La forma recomendada de ejecutar el proyecto es mediante Docker.

- Git.
- Docker Desktop con Docker Compose v2.
- Puertos locales `8000` y `8501` disponibles.
- Opcional: Python 3.12 para ejecutar herramientas fuera de Docker.

En Windows, asegurate de que Docker Desktop esté iniciado antes de continuar.

## Instalación paso a paso

### 1. Clonar el repositorio

```powershell
git clone https://github.com/No-Country-simulation/G10-ONE-equipo-14.git
Set-Location G10-ONE-equipo-14
```

Si `develop` contiene trabajo más reciente que `main`:

```powershell
git switch develop
git pull --ff-only origin develop
```

### 2. Crear la configuración local

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Linux/macOS:

```bash
cp .env.example .env
```

Los valores de `.env.example` sirven exclusivamente para desarrollo local. El archivo `.env` está ignorado por Git; nunca se deben subir credenciales, tokens ni secretos de OCI o proveedores de IA.

Variables disponibles:

| Variable | Uso | Valor local de ejemplo |
| --- | --- | --- |
| `APP_NAME` | Nombre visible de la API | `CommunityLab API` |
| `API_SCHEMA_VERSION` | Versión del contrato | `v1` |
| `ENVIRONMENT` | Entorno | `development` |
| `DATABASE_URL` | Conexión interna desde la API | PostgreSQL del servicio `db` |
| `API_URL` | Conexión interna desde Streamlit | `http://api:8000` |
| `MUTATIONS_ENABLED` | Habilita carga, edición, aprobación y publicación | `true` sólo en entornos controlados |
| `API_WRITE_KEY` | Secreto compartido enviado como `X-API-Key` | Sin valor en desarrollo local |
| `MUTATION_RATE_LIMIT` | Máximo de mutaciones por cliente y ventana | `60` |
| `MUTATION_RATE_WINDOW_SECONDS` | Duración de la ventana del límite | `60` |
| `ANALYSIS_PROVIDER` | Proveedor de análisis | `mock` |
| `GEMINI_API_KEY` | Secreto requerido sólo para Gemini | Sin valor |
| `STORAGE_BACKEND` | Adaptador de publicación | `local` |
| `POSTGRES_DB` | Base de datos local | `communitylab` |
| `POSTGRES_USER` | Usuario local | `communitylab` |
| `POSTGRES_PASSWORD` | Contraseña local | `communitylab` |

### Protección de la API pública

Las rutas de lectura (`health`, ejecuciones, activos y alertas) permanecen públicas. Las rutas que cambian datos pasan por tres controles: el interruptor `MUTATIONS_ENABLED`, una clave opcional `API_WRITE_KEY` comparada de forma segura y un límite por IP para cada ventana. El Blueprint de Render deja la demo pública en modo sólo lectura. Para habilitar curaduría en un entorno compartido, configure el mismo `API_WRITE_KEY` como secreto en la API y el dashboard y cambie `MUTATIONS_ENABLED=true`.

CORS acepta únicamente los orígenes definidos en `CORS_ORIGINS`; por defecto son las dos variantes locales de Streamlit. En un despliegue se debe agregar explícitamente el dominio real del dashboard. El limitador incluido vive en memoria y cubre el despliegue gratuito de una instancia; al escalar a varias réplicas debe reemplazarse por un contador compartido (por ejemplo Redis o el gateway de la plataforma).

### Entrada automática por webhook

`POST /api/v1/webhooks/interactions` recibe un evento normalizado desde n8n, Discord, Slack u otra fuente. `source + event_id` forma la clave idempotente: un reintento devuelve el mismo run y reutilizar el identificador con otro contenido devuelve HTTP 409. El endpoint pasa por los mismos controles de mutación (`MUTATIONS_ENABLED`, `X-API-Key` y rate limiting) y ejecuta exactamente el pipeline de la carga manual.

El contrato, ejemplo `curl` y los mapeos recomendados están en
[`docs/WEBHOOK_INTEGRATION.md`](docs/WEBHOOK_INTEGRATION.md). Ningún token de
Discord/Slack/n8n se guarda en CommunityLab.

### 3. Construir e iniciar la aplicación

```powershell
docker compose up -d --build
```

El inicio ocurre en este orden:

1. PostgreSQL inicia y pasa su health check.
2. La API ejecuta `python -m alembic upgrade head`.
3. FastAPI inicia solamente si las migraciones finalizan correctamente.
4. Streamlit y el worker inician cuando la API está saludable.

Verificar los servicios:

```powershell
docker compose ps
```

El resultado esperado es `Up` para los cuatro servicios y `healthy` para `db` y `api`.

### Procesamiento asíncrono de lotes

`POST /api/v1/process/async` acepta el mismo contrato que `/process`, exige
`Idempotency-Key` y responde inmediatamente con `job_id` y `status_url`. El
worker reclama los trabajos mediante bloqueo PostgreSQL `SKIP LOCKED`; el estado
se consulta en `GET /api/v1/jobs/{job_id}` hasta `SUCCEEDED` o `FAILED`.

El endpoint síncrono se conserva para integraciones compatibles. Para medir el
lote máximo con el proveedor mock reproducible:

```powershell
docker compose exec -T api python scripts/benchmark_500.py --api-url http://localhost:8000 --count 500 --async-mode --max-seconds 1
```

### Evaluación de calidad

La muestra humana, las definiciones de validez, grounding y precisión, y sus
limitaciones están en [`docs/EVALUATION_GUIDE.md`](docs/EVALUATION_GUIDE.md).
La línea base se reproduce sin red con:

```powershell
docker compose run --rm -T api python -m scripts.evaluate_quality
```

Los canales posteriores al MVP y su orden de implementación están definidos en
[`docs/CHANNEL_ROADMAP.md`](docs/CHANNEL_ROADMAP.md). Esa decisión no implica que
X/Twitter, newsletter, highlights o informes de sentimiento ya estén activos.

### 4. Abrir la aplicación

- Dashboard: [http://localhost:8501](http://localhost:8501)
- Swagger/OpenAPI: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health check: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

### 5. Ejecutar la demostración

1. Abrir el dashboard.
2. Mantener o cambiar la organización, comunidad y período de referencia.
3. Seleccionar uno de estos archivos:
   - `data/sample_interactions.json`
   - `data/sample_interactions.csv`
4. Presionar **Procesar archivo**.
5. Confirmar el resumen de recibidas, aceptadas, duplicadas y errores.
6. Volver a cargar el mismo archivo. La segunda carga debe informar los registros como duplicados para esa comunidad.
7. Copiar el `Run ID`, recargar el navegador y usar **Buscar ejecución** para recuperar el mismo resultado desde PostgreSQL.

Las pestañas permiten inspeccionar el análisis, las oportunidades y los activos
generados por la ejecución. **LinkedIn y FAQ** consulta su cola directamente en
PostgreSQL mediante la API; los pendientes continúan visibles después de
recargar el navegador o iniciar otra sesión. El botón **Actualizar cola** fuerza
una nueva consulta. Cada análisis y activo incluye una sección **Evidencia y
fuentes** con los extractos originales y sus identificadores de interacción.
El resumen de cada ejecución incluye además el sentimiento predominante, los
tres temas más frecuentes y el tiempo total de procesamiento en milisegundos.

La curaduría aplica una máquina de estados explícita: sólo un activo
`PENDING_REVIEW` puede aprobarse o rechazarse. Editar un activo `REJECTED`
crea una nueva versión y lo devuelve a `PENDING_REVIEW`; un activo `APPROVED`
es inmutable. Publicar nuevamente un activo aprobado es idempotente y devuelve
el manifest ya creado, sin generar registros duplicados.

## Endpoints de la API

| Método | Ruta | Estado actual |
| --- | --- | --- |
| `GET` | `/api/v1/health` | Implementado |
| `POST` | `/api/v1/process` | Ingesta JSON implementada |
| `POST` | `/api/v1/process/csv` | Ingesta CSV implementada |
| `POST` | `/api/v1/process/async` | Encola lotes para el worker durable |
| `GET` | `/api/v1/jobs/{job_id}` | Consulta el estado del procesamiento asíncrono |
| `POST` | `/api/v1/webhooks/interactions` | Entrada automática protegida e idempotente |
| `GET` | `/api/v1/runs/{run_id}` | Implementado |
| `GET` | `/api/v1/assets` | Implementado |
| `GET` | `/api/v1/alerts` | Alertas internas abiertas |
| `PATCH` | `/api/v1/assets/{asset_id}` | Implementado |
| `POST` | `/api/v1/assets/{asset_id}/approve` | Implementado |
| `POST` | `/api/v1/assets/{asset_id}/reject` | Implementado |
| `POST` | `/api/v1/assets/{asset_id}/publish` | Implementado |

Todas las rutas versionadas usan el prefijo `/api/v1`.

### Privacidad de las interacciones

Cada interacción admite `publication_consent` y `opt_out` (ambos `false` por
defecto). Correos y teléfonos se sustituyen por `[EMAIL]` y `[PHONE]` antes de
persistir o enviar texto al proveedor de IA. Sin consentimiento, las menciones
del autor se sustituyen por `[PERSON]`; con `opt_out: true` se conserva la
trazabilidad de la decisión, pero no se genera ningún activo publicable. Las
mismas columnas pueden incluirse de forma opcional en archivos CSV.

Las FAQ no se generan por una consulta aislada. El pipeline agrupa únicamente
interacciones de tipo `question` por su tema principal y genera una sola FAQ
cuando el grupo alcanza `FAQ_RECURRENCE_THRESHOLD` (2 por defecto). El activo
resultante conserva la evidencia y los identificadores de todas las preguntas
del grupo.

Las interacciones con sentimiento negativo o frustración siguen una ruta
interna: crean una alerta persistente, dejan la oportunidad bloqueada y no
generan activos públicos. El dashboard las presenta en **Alertas internas**, de
forma separada de oportunidades y de la cola de curaduría.

Los errores del dashboard se presentan como mensajes controlados. Cuando la
API devuelve un `detail` de FastAPI se muestra ese texto; timeouts, problemas
de conexión y respuestas no JSON reciben mensajes seguros sin detener la
sesión de Streamlit.

## Proveedor de análisis

El proveedor se selecciona con `ANALYSIS_PROVIDER`:

- `mock`: valor predeterminado para desarrollo local y pruebas reproducibles.
- `gemini`: proveedor real con salida JSON estructurada y evidencia textual verificada.

Para Gemini, configurar `GEMINI_API_KEY` como secreto del entorno y, opcionalmente, `GEMINI_MODEL`. La clave nunca debe guardarse en `.env.example`, GitHub ni imágenes. El fallback a `mock` sólo se activa explícitamente con `ANALYSIS_FALLBACK_PROVIDER=mock`; no está habilitado por defecto para evitar que una falla externa simule silenciosamente un análisis real.

## Objetos de base de datos

Las migraciones se encuentran en `alembic/versions/`.

### Tabla `interactions`

Guarda la interacción normalizada y su trazabilidad:

- UUID como clave primaria.
- Organización y comunidad.
- Identificador externo opcional.
- Autor, canal, tipo y texto.
- Fingerprint SHA-256.
- Fecha del evento y fecha de creación.
- Restricciones de unicidad por `external_id` y fingerprint dentro de cada comunidad.

### Tabla `runs`

Guarda cada solicitud de procesamiento:

- UUID de ejecución.
- Organización y comunidad.
- Clave de idempotencia.
- Hash de la solicitud.
- Estado y respuesta JSON.
- Fechas de creación y actualización.
- Unicidad de la clave de idempotencia por comunidad.

La API aplica automáticamente todas las migraciones pendientes al iniciar. Para consultar las tablas:

```powershell
docker compose exec db psql -U communitylab -d communitylab -c "\dt"
docker compose exec db psql -U communitylab -d communitylab -c "SELECT count(*) FROM interactions;"
docker compose exec db psql -U communitylab -d communitylab -c "SELECT id, status, created_at FROM runs ORDER BY created_at DESC;"
```

No ejecutar `alembic downgrade` sobre una base con información importante sin respaldo.

### Controles de calidad en CI

Cada PR y push ejecuta pruebas, migraciones, validación Terraform, Ruff como lint/análisis estático, formato de los archivos Python modificados, `pip-audit` y compilación de los módulos del dashboard. Los pushes a `main` agregan un smoke test sobre el health de la API y el dashboard público de Render. Para reproducir los controles de calidad:

```bash
python -m pip install -r requirements-dev.txt
ruff check app dashboard tests
pip-audit -r requirements.txt
python -m py_compile dashboard/app.py dashboard/api_client.py
```

### Respaldo y restauración de PostgreSQL

Con la base local activa, genere un dump autocontenido y compruébelo en una base temporal aislada:

```bash
backup_path="$(sh deploy/backup.sh)"
sh deploy/verify-backup.sh "$backup_path"
```

`backup.sh` produce un archivo en formato custom de PostgreSQL, comprueba que su catálogo sea legible y aplica una retención de siete días. `verify-backup.sh` crea una base con nombre único, restaura con `--exit-on-error`, verifica la revisión Alembic, las tablas principales y los conteos de registros, y siempre elimina la base temporal. No apunta la restauración a la base original.

Para producción, configure `BACKUP_DIR` en un volumen persistente o copie el resultado cifrado a almacenamiento externo. La base gratuita de Render no constituye una estrategia de retención: programe el backup fuera del servicio antes de su vencimiento. Puede ajustar `COMPOSE_FILE_PATH`, `POSTGRES_USER`, `POSTGRES_DB` y `BACKUP_RETENTION_DAYS` sin modificar los scripts.

## Pruebas

El CI utiliza una base PostgreSQL aislada llamada `communitylab_test` y verifica migraciones y pruebas.

Para repetir la suite dentro de Docker:

```powershell
docker compose exec db createdb -U communitylab communitylab_test
docker compose exec -e TEST_DATABASE_URL=postgresql+psycopg://communitylab:communitylab@db:5432/communitylab_test api python -m pytest -q tests
```

Si la base de pruebas ya existe, el primer comando puede indicar que está duplicada; se puede continuar con el segundo comando.

Para ejecutar las pruebas fuera de Docker:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:TEST_DATABASE_URL = "postgresql+psycopg://communitylab:communitylab@localhost:5432/communitylab_test"
python -m pytest -q tests
```

La variante fuera de Docker requiere un PostgreSQL accesible desde el host. La opción dentro de Docker es la recomendada.

## Comandos operativos

Ver logs:

```powershell
docker compose logs -f api dashboard
```

Reiniciar servicios detenidos:

```powershell
docker compose up -d
```

Detener la aplicación conservando los datos:

```powershell
docker compose down
```

Reconstruir después de cambiar dependencias o Dockerfiles:

```powershell
docker compose up -d --build
```

## Solución de problemas

### No abre `http://localhost:8501`

```powershell
docker compose ps -a
docker compose up -d
docker compose logs --tail 100 dashboard
```

Si Docker Desktop se reinicia, los contenedores pueden quedar detenidos y deben iniciarse nuevamente con `docker compose up -d`.

### No abre la API

```powershell
docker compose logs --tail 100 db api
```

La API espera que PostgreSQL esté saludable y que Alembic pueda aplicar las migraciones.

### Los puertos 8000 o 8501 están ocupados

Detener el proceso que usa el puerto o cambiar el puerto del lado izquierdo en `docker-compose.yml`. Por ejemplo, `8502:8501` permite abrir Streamlit en `http://localhost:8502`.

### Limpiar completamente la base local

El siguiente comando elimina también el volumen con los datos locales:

```powershell
docker compose down -v
```

Usarlo solamente cuando la información local pueda descartarse.

## Cómo continuar el desarrollo

1. Actualizar `develop`:

   ```powershell
   git switch develop
   git pull --ff-only origin develop
   ```

2. Crear una rama corta desde `develop`:

   ```powershell
   git switch -c feature/COMLAB-XX-descripcion
   ```

3. Implementar una tarea acotada y agregar pruebas.
4. Ejecutar la suite y verificar Docker Compose.
5. Crear un commit descriptivo y subir la rama:

   ```powershell
   git add .
   git commit -m "feat: descripcion del cambio"
   git push -u origin feature/COMLAB-XX-descripcion
   ```

6. Abrir un pull request hacia `develop` y enlazar Jira/GitHub.
7. Integrar `develop` en `main` solamente cuando la versión esté estable y demostrable.

Reglas adicionales: [CONTRIBUTING.md](CONTRIBUTING.md) y [docs/GIT_WORKFLOW.md](docs/GIT_WORKFLOW.md).

## Gestión del proyecto

- Código: [repositorio de GitHub](https://github.com/No-Country-simulation/G10-ONE-equipo-14)
- Backlog: [proyecto CommunityLab en Jira](https://g10-latam-equipo14.atlassian.net/jira/software/projects/COMLAB/boards/1)
- Documentación funcional: carpeta [`docs`](docs)
- Especificación fundacional del MVP: [docs/CommunityLab_MVP.pdf](docs/CommunityLab_MVP.pdf)
- Roadmap y proceso por etapas: [docs/ROADMAP_ETAPAS.md](docs/ROADMAP_ETAPAS.md)
- Guion de demo y cierre: [docs/DEMO_GUIDE.md](docs/DEMO_GUIDE.md)
- Prueba funcional paso a paso: [docs/sets_pruebas/GUIA_PRUEBA_FUNCIONAL.md](docs/sets_pruebas/GUIA_PRUEBA_FUNCIONAL.md)
- Manual de usuario: [docs/MANUAL_USUARIO.md](docs/MANUAL_USUARIO.md)
- Evidencias visuales: [docs/evidence](docs/evidence)
- Entregable técnico E1–E8: [docs/ENTREGABLE_IMPLEMENTACION_E1_E8.md](docs/ENTREGABLE_IMPLEMENTACION_E1_E8.md)
- Acta de cierre y continuidad: [docs/CIERRE_ETAPA_2026-10-17.md](docs/CIERRE_ETAPA_2026-10-17.md)
- Inventario auditado y brechas pendientes: [docs/INVENTARIO_PROYECTO.md](docs/INVENTARIO_PROYECTO.md)

Antes de empezar una tarea, revisar el backlog para evitar duplicar trabajo y mantener el ticket relacionado actualizado.

## Seguridad

- Nunca subir `.env`, credenciales, claves API ni archivos de configuración de OCI.
- Utilizar credenciales diferentes para producción.
- Mantener PostgreSQL sin publicar al host salvo que una tarea local lo requiera.
- Revisar cualquier dato de comunidad antes de utilizarlo con proveedores externos de IA.

## Licencia

El repositorio todavía no contiene un archivo de licencia. Antes de distribuirlo fuera del equipo, definir y agregar la licencia correspondiente.
