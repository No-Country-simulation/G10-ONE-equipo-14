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
- PostgreSQL 16 con migraciones Alembic automáticas.
- Dashboard Streamlit para cargar archivos y visualizar el resultado.
- Health checks de PostgreSQL y API.
- Logs JSON para solicitudes, análisis/reintentos y almacenamiento, sin contenido sensible.
- Pipeline de análisis, detección de PII y oportunidades.
- Generación versionada de activos LinkedIn y FAQ.
- FAQ basada en recurrencia temática, con umbral configurable.
- Curaduría persistente: edición, aprobación y rechazo.
- Adaptadores de almacenamiento local y OCI con manifiestos verificables.
- Suite de 93 pruebas aprobadas, 1 omitida y CI en GitHub Actions al cierre E8.
- Datos de demostración en JSON y CSV.

### Próximos pasos operativos

- Migrar o recrear PostgreSQL antes del vencimiento del plan gratuito de Render.
- Configurar credenciales OCI sólo en el entorno que deba publicar objetos de forma persistente.
- Capturar retrospectivamente evidencias visuales de E1–E6 si el proceso académico exige una imagen por etapa.

## Arquitectura

Flujo actual:

```text
JSON/CSV -> Streamlit -> FastAPI/Pydantic -> normalización y fingerprint
         -> PostgreSQL (interactions + runs) -> resumen de la ejecución
```

Flujo objetivo:

```text
JSON/CSV -> FastAPI -> PostgreSQL -> LangGraph/LLM -> oportunidades
         -> activos LinkedIn/FAQ -> curaduría humana -> OCI Object Storage
```

Servicios Docker:

| Servicio | Tecnología | Dirección local | Responsabilidad |
| --- | --- | --- | --- |
| `db` | PostgreSQL 16 | red interna de Docker | Interacciones, ejecuciones e idempotencia |
| `api` | FastAPI | `http://localhost:8000` | Contratos, ingesta y persistencia |
| `dashboard` | Streamlit | `http://localhost:8501` | Demostración visual y carga de archivos |

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

### Protección de la API pública

Las rutas de lectura (`health`, ejecuciones, activos y alertas) permanecen públicas. Las rutas que cambian datos pasan por tres controles: el interruptor `MUTATIONS_ENABLED`, una clave opcional `API_WRITE_KEY` comparada de forma segura y un límite por IP para cada ventana. El Blueprint de Render deja la demo pública en modo sólo lectura. Para habilitar curaduría en un entorno compartido, configure el mismo `API_WRITE_KEY` como secreto en la API y el dashboard y cambie `MUTATIONS_ENABLED=true`.

CORS acepta únicamente los orígenes definidos en `CORS_ORIGINS`; por defecto son las dos variantes locales de Streamlit. En un despliegue se debe agregar explícitamente el dominio real del dashboard. El limitador incluido vive en memoria y cubre el despliegue gratuito de una instancia; al escalar a varias réplicas debe reemplazarse por un contador compartido (por ejemplo Redis o el gateway de la plataforma).

### Entrada automática por webhook

`POST /api/v1/webhooks/interactions` recibe un evento normalizado desde n8n, Discord, Slack u otra fuente. `source + event_id` forma la clave idempotente: un reintento devuelve el mismo run y reutilizar el identificador con otro contenido devuelve HTTP 409. El endpoint pasa por los mismos controles de mutación (`MUTATIONS_ENABLED`, `X-API-Key` y rate limiting) y ejecuta exactamente el pipeline de la carga manual.

El contrato, ejemplo `curl` y los mapeos recomendados están en [`docs/WEBHOOK_INTEGRATION.md`](docs/WEBHOOK_INTEGRATION.md). Ningún token de Discord/Slack/n8n se guarda en CommunityLab.
| `POSTGRES_DB` | Base de datos local | `communitylab` |
| `POSTGRES_USER` | Usuario local | `communitylab` |
| `POSTGRES_PASSWORD` | Contraseña local | `communitylab` |

### 3. Construir e iniciar la aplicación

```powershell
docker compose up -d --build
```

El inicio ocurre en este orden:

1. PostgreSQL inicia y pasa su health check.
2. La API ejecuta `python -m alembic upgrade head`.
3. FastAPI inicia solamente si las migraciones finalizan correctamente.
4. Streamlit inicia cuando la API está saludable.

Verificar los servicios:

```powershell
docker compose ps
```

El resultado esperado es `Up` para los tres servicios y `healthy` para `db` y `api`.

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
- Roadmap y proceso por etapas: [docs/ROADMAP_ETAPAS.md](docs/ROADMAP_ETAPAS.md)
- Guion de demo y cierre: [docs/DEMO_GUIDE.md](docs/DEMO_GUIDE.md)
- Evidencias visuales: [docs/evidence](docs/evidence)
- Entregable técnico E1–E8: [docs/ENTREGABLE_IMPLEMENTACION_E1_E8.md](docs/ENTREGABLE_IMPLEMENTACION_E1_E8.md)
- Inventario auditado y brechas pendientes: [docs/INVENTARIO_PROYECTO.md](docs/INVENTARIO_PROYECTO.md)

Antes de empezar una tarea, revisar el backlog para evitar duplicar trabajo y mantener el ticket relacionado actualizado.

## Seguridad

- Nunca subir `.env`, credenciales, claves API ni archivos de configuración de OCI.
- Utilizar credenciales diferentes para producción.
- Mantener PostgreSQL sin publicar al host salvo que una tarea local lo requiera.
- Revisar cualquier dato de comunidad antes de utilizarlo con proveedores externos de IA.

## Licencia

El repositorio todavía no contiene un archivo de licencia. Antes de distribuirlo fuera del equipo, definir y agregar la licencia correspondiente.
