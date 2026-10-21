# CommunityLab

Motor inteligente de transformaciÃ³n y distribuciÃ³n para comunidades digitales, desarrollado por **G10 Â· Hackathon ONE Â· Equipo 14**.

CommunityLab recibe interacciones en JSON o CSV, las normaliza, deduplica y guarda en PostgreSQL. El pipeline analiza las interacciones, detecta oportunidades, genera activos LinkedIn/FAQ y permite curarlos antes de su publicaciÃ³n mediante un adaptador de almacenamiento.

## Demo pÃºblica

- AplicaciÃ³n: https://communitylab-dashboard.onrender.com
- API: https://communitylab-api.onrender.com
- Swagger/OpenAPI: https://communitylab-api.onrender.com/docs
- Health: https://communitylab-api.onrender.com/api/v1/health

El entorno estÃ¡ desplegado con el plan gratuito de Render y puede tardar cerca de un minuto en despertar despuÃ©s de un perÃ­odo sin actividad. La base gratuita de demostraciÃ³n expira a los 30 dÃ­as.

## Estado del proyecto

### Implementado

- API REST con FastAPI y contratos versionados con Pydantic.
- Carga de interacciones JSON y CSV.
- NormalizaciÃ³n, fingerprint SHA-256 y deduplicaciÃ³n por comunidad.
- Idempotencia persistida mediante el encabezado `Idempotency-Key`.
- Cola asÃ­ncrona durable en PostgreSQL y worker independiente para lotes grandes.
- PostgreSQL 16 con migraciones Alembic automÃ¡ticas.
- Dashboard Streamlit para cargar archivos y visualizar el resultado.
- Health checks de PostgreSQL y API.
- Logs JSON para solicitudes, anÃ¡lisis/reintentos y almacenamiento, sin contenido sensible.
- Pipeline de anÃ¡lisis, detecciÃ³n de PII y oportunidades.
- GeneraciÃ³n versionada de activos LinkedIn y FAQ.
- FAQ basada en recurrencia temÃ¡tica, con umbral configurable.
- CuradurÃ­a persistente: ediciÃ³n, aprobaciÃ³n y rechazo.
- Interfaz visual con identidad de CommunityLab, ayuda contextual y separaciÃ³n
  explÃ­cita entre controles editables e informaciÃ³n de solo lectura.
- Adaptadores de almacenamiento local y OCI con manifiestos verificables.
- Suite de **159 pruebas aprobadas** y CI en GitHub Actions.
- Datos de demostraciÃ³n en JSON y CSV.

### Ãšltimo cierre verificado

El 17 de octubre de 2026 se publicÃ³ en `main` la mejora visual y de ayuda del
dashboard mediante los PR [#220](https://github.com/No-Country-simulation/G10-ONE-equipo-14/pull/220)
y [#221](https://github.com/No-Country-simulation/G10-ONE-equipo-14/pull/221).
La ejecuciÃ³n de CI de producciÃ³n
[#38999088448](https://github.com/No-Country-simulation/G10-ONE-equipo-14/actions/runs/38999088448)
aprobÃ³ calidad, Terraform, 159 pruebas y smoke tests pÃºblicos. La versiÃ³n
desplegada se verificÃ³ ademÃ¡s en navegador, con API y PostgreSQL operativos y
sin errores de consola.

### Trabajo deliberadamente pendiente

- Migrar o recrear PostgreSQL antes del vencimiento del plan gratuito de Render.
- Ejecutar INV-002 a INV-005 durante el despliegue final: activar OCI, completar
  layout y manifest, y mostrar el recibo de publicaciÃ³n en Streamlit.
- Configurar credenciales OCI Ãºnicamente en ese entorno; nunca en el repositorio.

Todos los puntos funcionales no OCI del inventario estÃ¡n completados. La
trazabilidad del cierre y los cuatro pendientes deliberados se detallan en
[`docs/INVENTARIO_PROYECTO.md`](docs/INVENTARIO_PROYECTO.md).

## Arquitectura

Flujo implementado:

Con Gemini, cada bloque de la carga se envía en una sola solicitud estructurada
para obtener sentimiento, temas, entidades y borradores LinkedIn/FAQ. Los bloques
se limitan aproximadamente a 60.000 caracteres; una carga mayor requiere varias
solicitudes. El backend valida evidencia y reglas de oportunidad antes de guardar
los borradores para revisión.

```text
JSON/CSV o webhook -> FastAPI/Pydantic -> normalizaciÃ³n, privacidad y fingerprint
                    -> PostgreSQL -> anÃ¡lisis mock/Gemini -> oportunidades o alertas
                    -> activos LinkedIn/FAQ -> curadurÃ­a humana
                    -> almacenamiento local u OCI mediante adaptador
```

Los lotes grandes pueden ingresar por la cola asÃ­ncrona durable y ser procesados
por el worker. La demostraciÃ³n pÃºblica usa almacenamiento local efÃ­mero y deja
las mutaciones deshabilitadas; la activaciÃ³n final de OCI sigue registrada como
trabajo pendiente.

Servicios Docker:

| Servicio | TecnologÃ­a | DirecciÃ³n local | Responsabilidad |
| --- | --- | --- | --- |
| `db` | PostgreSQL 16 | red interna de Docker | Interacciones, ejecuciones e idempotencia |
| `api` | FastAPI | `http://localhost:8000` | Contratos, ingesta y persistencia |
| `dashboard` | Streamlit | `http://localhost:8501` | DemostraciÃ³n visual y carga de archivos |
| `worker` | Python/FastAPI services | red interna de Docker | Procesamiento asÃ­ncrono durable de lotes |

## Estructura del repositorio

```text
.
â”œâ”€â”€ alembic/                 # ConfiguraciÃ³n y migraciones de PostgreSQL
â”‚   â””â”€â”€ versions/
â”œâ”€â”€ app/
â”‚   â”œâ”€â”€ api/v1/endpoints/    # Rutas FastAPI
â”‚   â”œâ”€â”€ core/                # ConfiguraciÃ³n de la aplicaciÃ³n
â”‚   â”œâ”€â”€ db/models/           # Modelos SQLAlchemy
â”‚   â”œâ”€â”€ domain/              # Reglas de dominio y fingerprint
â”‚   â”œâ”€â”€ schemas/v1/          # Contratos Pydantic versionados
â”‚   â””â”€â”€ services/            # Ingesta, CSV, normalizaciÃ³n e idempotencia
â”œâ”€â”€ dashboard/               # Frontend Streamlit y su Dockerfile
â”œâ”€â”€ data/                    # Archivos JSON/CSV de demostraciÃ³n
â”œâ”€â”€ docs/                    # DocumentaciÃ³n funcional y tÃ©cnica
â”œâ”€â”€ tests/                   # Pruebas unitarias, contrato e integraciÃ³n
â”œâ”€â”€ .env.example             # Variables locales de ejemplo
â”œâ”€â”€ docker-compose.yml       # OrquestaciÃ³n local
â”œâ”€â”€ Dockerfile               # Imagen de la API
â””â”€â”€ requirements.txt         # Dependencias del backend
```

## Requisitos

La forma recomendada de ejecutar el proyecto es mediante Docker.

- Git.
- Docker Desktop con Docker Compose v2.
- Puertos locales `8000` y `8501` disponibles.
- Opcional: Python 3.12 para ejecutar herramientas fuera de Docker.

En Windows, asegurate de que Docker Desktop estÃ© iniciado antes de continuar.

## InstalaciÃ³n paso a paso

### 1. Clonar el repositorio

```powershell
git clone https://github.com/No-Country-simulation/G10-ONE-equipo-14.git
Set-Location G10-ONE-equipo-14
```

Si `develop` contiene trabajo mÃ¡s reciente que `main`:

```powershell
git switch develop
git pull --ff-only origin develop
```

### 2. Crear la configuraciÃ³n local

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Linux/macOS:

```bash
cp .env.example .env
```

Los valores de `.env.example` sirven exclusivamente para desarrollo local. El archivo `.env` estÃ¡ ignorado por Git; nunca se deben subir credenciales, tokens ni secretos de OCI o proveedores de IA.

Variables disponibles:

| Variable | Uso | Valor local de ejemplo |
| --- | --- | --- |
| `APP_NAME` | Nombre visible de la API | `CommunityLab API` |
| `API_SCHEMA_VERSION` | VersiÃ³n del contrato | `v1` |
| `ENVIRONMENT` | Entorno | `development` |
| `DATABASE_URL` | ConexiÃ³n interna desde la API | PostgreSQL del servicio `db` |
| `API_URL` | ConexiÃ³n interna desde Streamlit | `http://api:8000` |
| `MUTATIONS_ENABLED` | Habilita carga, ediciÃ³n, aprobaciÃ³n y publicaciÃ³n | `true` sÃ³lo en entornos controlados |
| `API_WRITE_KEY` | Secreto compartido enviado como `X-API-Key` | Sin valor en desarrollo local |
| `MUTATION_RATE_LIMIT` | MÃ¡ximo de mutaciones por cliente y ventana | `60` |
| `MUTATION_RATE_WINDOW_SECONDS` | DuraciÃ³n de la ventana del lÃ­mite | `60` |
| `ANALYSIS_PROVIDER` | Proveedor para analisis y generacion de LinkedIn/FAQ | `gemini` en `.env.example`; `mock` sin configuracion |
| `GEMINI_API_KEY` | Secreto requerido sÃ³lo para Gemini | Sin valor |
| `STORAGE_BACKEND` | Adaptador de publicaciÃ³n | `local` |
| `POSTGRES_DB` | Base de datos local | `communitylab` |
| `POSTGRES_USER` | Usuario local | `communitylab` |
| `POSTGRES_PASSWORD` | ContraseÃ±a local | `communitylab` |

### ProtecciÃ³n de la API pÃºblica

Las rutas de lectura (`health`, ejecuciones, activos y alertas) permanecen pÃºblicas. Las rutas que cambian datos pasan por tres controles: el interruptor `MUTATIONS_ENABLED`, una clave opcional `API_WRITE_KEY` comparada de forma segura y un lÃ­mite por IP para cada ventana. El Blueprint de Render deja la demo pÃºblica en modo sÃ³lo lectura. Para habilitar curadurÃ­a en un entorno compartido, configure el mismo `API_WRITE_KEY` como secreto en la API y el dashboard y cambie `MUTATIONS_ENABLED=true`.

CORS acepta Ãºnicamente los orÃ­genes definidos en `CORS_ORIGINS`; por defecto son las dos variantes locales de Streamlit. En un despliegue se debe agregar explÃ­citamente el dominio real del dashboard. El limitador incluido vive en memoria y cubre el despliegue gratuito de una instancia; al escalar a varias rÃ©plicas debe reemplazarse por un contador compartido (por ejemplo Redis o el gateway de la plataforma).

### Entrada automÃ¡tica por webhook

`POST /api/v1/webhooks/interactions` recibe un evento normalizado desde n8n, Discord, Slack u otra fuente. `source + event_id` forma la clave idempotente: un reintento devuelve el mismo run y reutilizar el identificador con otro contenido devuelve HTTP 409. El endpoint pasa por los mismos controles de mutaciÃ³n (`MUTATIONS_ENABLED`, `X-API-Key` y rate limiting) y ejecuta exactamente el pipeline de la carga manual.

El contrato, ejemplo `curl` y los mapeos recomendados estÃ¡n en
[`docs/WEBHOOK_INTEGRATION.md`](docs/WEBHOOK_INTEGRATION.md). NingÃºn token de
Discord/Slack/n8n se guarda en CommunityLab.

### 3. Construir e iniciar la aplicaciÃ³n

```powershell
docker compose up -d --build
```

El inicio ocurre en este orden:

1. PostgreSQL inicia y pasa su health check.
2. La API ejecuta `python -m alembic upgrade head`.
3. FastAPI inicia solamente si las migraciones finalizan correctamente.
4. Streamlit y el worker inician cuando la API estÃ¡ saludable.

Verificar los servicios:

```powershell
docker compose ps
```

El resultado esperado es `Up` para los cuatro servicios y `healthy` para `db` y `api`.

### Procesamiento asÃ­ncrono de lotes

`POST /api/v1/process/async` acepta el mismo contrato que `/process`, exige
`Idempotency-Key` y responde inmediatamente con `job_id` y `status_url`. El
worker reclama los trabajos mediante bloqueo PostgreSQL `SKIP LOCKED`; el estado
se consulta en `GET /api/v1/jobs/{job_id}` hasta `SUCCEEDED` o `FAILED`.

El endpoint sÃ­ncrono se conserva para integraciones compatibles. Para medir el
lote mÃ¡ximo con el proveedor mock reproducible:

```powershell
docker compose exec -T api python scripts/benchmark_500.py --api-url http://localhost:8000 --count 500 --async-mode --max-seconds 1
```

### EvaluaciÃ³n de calidad

La muestra humana, las definiciones de validez, grounding y precisiÃ³n, y sus
limitaciones estÃ¡n en [`docs/EVALUATION_GUIDE.md`](docs/EVALUATION_GUIDE.md).
La lÃ­nea base se reproduce sin red con:

```powershell
docker compose run --rm -T api python -m scripts.evaluate_quality
```

Los canales posteriores al MVP y su orden de implementaciÃ³n estÃ¡n definidos en
[`docs/CHANNEL_ROADMAP.md`](docs/CHANNEL_ROADMAP.md). Esa decisiÃ³n no implica que
X/Twitter, newsletter, highlights o informes de sentimiento ya estÃ©n activos.

### 4. Abrir la aplicaciÃ³n

- Dashboard: [http://localhost:8501](http://localhost:8501)
- Swagger/OpenAPI: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health check: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

### 5. Ejecutar la demostraciÃ³n

1. Abrir el dashboard.
2. Mantener o cambiar la organizaciÃ³n, comunidad y perÃ­odo de referencia.
3. Seleccionar uno de estos archivos:
   - `data/sample_interactions.json`
   - `data/sample_interactions.csv`
4. Presionar **Procesar archivo**.
5. Confirmar el resumen de recibidas, aceptadas, duplicadas, reprocesadas y errores.
6. Volver a seleccionar el mismo archivo. El dashboard debe permitir recuperar
   una ejecuciÃ³n anterior o procesarlo nuevamente. Si se reprocesa, crea un Run
   nuevo y vuelve a analizar las interacciones existentes sin insertar filas
   duplicadas.
7. En **Recuperar una ejecuciÃ³n**, filtrar por OrganizaciÃ³n o Comunidad y elegir
   la opciÃ³n identificada por nombre de archivo, fecha y Run ID. El ingreso
   manual del UUID queda disponible como alternativa.

Las pestanas permiten inspeccionar el analisis, las oportunidades y los activos generados por la ejecucion. La cola de curaduria tiene pestanas separadas para LinkedIn y FAQ y consulta PostgreSQL mediante la API; los borradores pendientes siguen visibles al recargar el navegador o iniciar otra sesion. El boton **Actualizar cola** fuerza una nueva consulta. Cada anÃ¡lisis y activo incluye una secciÃ³n **Evidencia y
fuentes** con los extractos originales y sus identificadores de interacciÃ³n.
El resumen de cada ejecuciÃ³n incluye ademÃ¡s el sentimiento predominante, los
tres temas mÃ¡s frecuentes y el tiempo total de procesamiento en milisegundos.

La curadurÃ­a aplica una mÃ¡quina de estados explÃ­cita: sÃ³lo un activo
`PENDING_REVIEW` puede aprobarse o rechazarse. Editar un activo `REJECTED`
crea una nueva versiÃ³n y lo devuelve a `PENDING_REVIEW`; un activo `APPROVED`
es inmutable. Publicar nuevamente un activo aprobado es idempotente y devuelve
el manifest ya creado, sin generar registros duplicados.

## Endpoints de la API

| MÃ©todo | Ruta | Estado actual |
| --- | --- | --- |
| `GET` | `/api/v1/health` | Implementado |
| `POST` | `/api/v1/process` | Ingesta JSON implementada |
| `POST` | `/api/v1/process/csv` | Ingesta CSV implementada |
| `POST` | `/api/v1/process/async` | Encola lotes para el worker durable |
| `GET` | `/api/v1/jobs/{job_id}` | Consulta el estado del procesamiento asÃ­ncrono |
| `POST` | `/api/v1/webhooks/interactions` | Entrada automÃ¡tica protegida e idempotente |
| `GET` | `/api/v1/runs/{run_id}` | Implementado |
| `GET` | `/api/v1/assets` | Implementado |
| `GET` | `/api/v1/alerts` | Alertas internas abiertas |
| `PATCH` | `/api/v1/assets/{asset_id}` | Implementado |
| `POST` | `/api/v1/assets/{asset_id}/approve` | Implementado |
| `POST` | `/api/v1/assets/{asset_id}/reject` | Implementado |
| `POST` | `/api/v1/assets/{asset_id}/publish` | Implementado |

Todas las rutas versionadas usan el prefijo `/api/v1`.

### Privacidad de las interacciones

Cada interacciÃ³n admite `publication_consent` y `opt_out` (ambos `false` por
defecto). Correos y telÃ©fonos se sustituyen por `[EMAIL]` y `[PHONE]`, las
menciones `@usuario` y el nombre del autor por `[PERSON]` antes de analizar o
redactar contenido. Los borradores de LinkedIn omiten el nombre del autor y no
reproducen literalmente la interaccion; siguen sujetos a curaduria humana.
Con `opt_out: true` se conserva la trazabilidad, pero no se genera ningÃºn
activo publicable. Las mismas columnas pueden incluirse de forma opcional en CSV.

Las FAQ no se generan por una consulta aislada. El pipeline agrupa interacciones de tipo `question` por tema y crea una propuesta cuando se alcanza `FAQ_RECURRENCE_THRESHOLD` (2 por defecto). Gemini redacta hasta cinco preguntas y respuestas propuestas basadas en las dudas recurrentes y evidencia del grupo. La propuesta conserva fuentes, se puede editar manualmente en la pestana FAQ y requiere revisi.n humana.

Las interacciones con sentimiento negativo o frustraciÃ³n siguen una ruta
interna: crean una alerta persistente, dejan la oportunidad bloqueada y no
generan activos pÃºblicos. El dashboard las presenta en **Alertas internas**, de
forma separada de oportunidades y de la cola de curadurÃ­a.

Los errores del dashboard se presentan como mensajes controlados. Cuando la
API devuelve un `detail` de FastAPI se muestra ese texto; timeouts, problemas
de conexiÃ³n y respuestas no JSON reciben mensajes seguros sin detener la
sesiÃ³n de Streamlit.

## Proveedor de anÃ¡lisis

El proveedor se selecciona con `ANALYSIS_PROVIDER`:

- `mock`: valor predeterminado para desarrollo local y pruebas reproducibles.
- `gemini`: anÃ¡lisis estructurado y redacciÃ³n libre de LinkedIn basada en evidencia anonimizada.

Para Gemini, configurar `GEMINI_API_KEY` como secreto del entorno y, opcionalmente, `GEMINI_MODEL`. LinkedIn se redacta libremente en cada ejecucion; el prompt solicita 150 a 300 palabras y se conserva la longitud que entregue el proveedor. El proveedor `mock` devuelve una muestra determinista para desarrollo, no una publicaciÃ³n de producciÃ³n. La clave nunca debe guardarse en `.env.example`, GitHub ni imÃ¡genes. El fallback a `mock` sÃ³lo se activa explÃ­citamente con `ANALYSIS_FALLBACK_PROVIDER=mock`; no estÃ¡ habilitado por defecto para evitar que una falla externa simule silenciosamente un anÃ¡lisis real.

## Objetos de base de datos

Las migraciones se encuentran en `alembic/versions/`.

### Tabla `interactions`

Guarda la interacciÃ³n normalizada y su trazabilidad:

- UUID como clave primaria.
- OrganizaciÃ³n y comunidad.
- Identificador externo opcional.
- Autor, canal, tipo y texto.
- Fingerprint SHA-256.
- Fecha del evento y fecha de creaciÃ³n.
- Restricciones de unicidad por `external_id` y fingerprint dentro de cada comunidad.

### Tabla `runs`

Guarda cada solicitud de procesamiento:

- UUID de ejecuciÃ³n.
- OrganizaciÃ³n y comunidad.
- Clave de idempotencia.
- Hash de la solicitud.
- Estado y respuesta JSON.
- Fechas de creaciÃ³n y actualizaciÃ³n.
- Unicidad de la clave de idempotencia por comunidad.

La API aplica automÃ¡ticamente todas las migraciones pendientes al iniciar. Para consultar las tablas:

```powershell
docker compose exec db psql -U communitylab -d communitylab -c "\dt"
docker compose exec db psql -U communitylab -d communitylab -c "SELECT count(*) FROM interactions;"
docker compose exec db psql -U communitylab -d communitylab -c "SELECT id, status, created_at FROM runs ORDER BY created_at DESC;"
```

No ejecutar `alembic downgrade` sobre una base con informaciÃ³n importante sin respaldo.

### Controles de calidad en CI

Cada PR y push ejecuta pruebas, migraciones, validaciÃ³n Terraform, Ruff como lint/anÃ¡lisis estÃ¡tico, formato de los archivos Python modificados, `pip-audit` y compilaciÃ³n de los mÃ³dulos del dashboard. Los pushes a `main` agregan un smoke test sobre el health de la API y el dashboard pÃºblico de Render. Para reproducir los controles de calidad:

```bash
python -m pip install -r requirements-dev.txt
ruff check app dashboard tests
pip-audit -r requirements.txt
python -m py_compile dashboard/app.py dashboard/api_client.py
```

### Respaldo y restauraciÃ³n de PostgreSQL

Con la base local activa, genere un dump autocontenido y compruÃ©belo en una base temporal aislada:

```bash
backup_path="$(sh deploy/backup.sh)"
sh deploy/verify-backup.sh "$backup_path"
```

`backup.sh` produce un archivo en formato custom de PostgreSQL, comprueba que su catÃ¡logo sea legible y aplica una retenciÃ³n de siete dÃ­as. `verify-backup.sh` crea una base con nombre Ãºnico, restaura con `--exit-on-error`, verifica la revisiÃ³n Alembic, las tablas principales y los conteos de registros, y siempre elimina la base temporal. No apunta la restauraciÃ³n a la base original.

Para producciÃ³n, configure `BACKUP_DIR` en un volumen persistente o copie el resultado cifrado a almacenamiento externo. La base gratuita de Render no constituye una estrategia de retenciÃ³n: programe el backup fuera del servicio antes de su vencimiento. Puede ajustar `COMPOSE_FILE_PATH`, `POSTGRES_USER`, `POSTGRES_DB` y `BACKUP_RETENTION_DAYS` sin modificar los scripts.

## Pruebas

El CI utiliza una base PostgreSQL aislada llamada `communitylab_test` y verifica migraciones y pruebas.

Para repetir la suite dentro de Docker:

```powershell
docker compose exec db createdb -U communitylab communitylab_test
docker compose exec -e TEST_DATABASE_URL=postgresql+psycopg://communitylab:communitylab@db:5432/communitylab_test api python -m pytest -q tests
```

Si la base de pruebas ya existe, el primer comando puede indicar que estÃ¡ duplicada; se puede continuar con el segundo comando.

Para ejecutar las pruebas fuera de Docker:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:TEST_DATABASE_URL = "postgresql+psycopg://communitylab:communitylab@localhost:5432/communitylab_test"
python -m pytest -q tests
```

La variante fuera de Docker requiere un PostgreSQL accesible desde el host. La opciÃ³n dentro de Docker es la recomendada.

## Comandos operativos

Ver logs:

```powershell
docker compose logs -f api dashboard
```

Reiniciar servicios detenidos:

```powershell
docker compose up -d
```

Detener la aplicaciÃ³n conservando los datos:

```powershell
docker compose down
```

Reconstruir despuÃ©s de cambiar dependencias o Dockerfiles:

```powershell
docker compose up -d --build
```

## SoluciÃ³n de problemas

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

La API espera que PostgreSQL estÃ© saludable y que Alembic pueda aplicar las migraciones.

### Los puertos 8000 o 8501 estÃ¡n ocupados

Detener el proceso que usa el puerto o cambiar el puerto del lado izquierdo en `docker-compose.yml`. Por ejemplo, `8502:8501` permite abrir Streamlit en `http://localhost:8502`.

### Limpiar completamente la base local

El siguiente comando elimina tambiÃ©n el volumen con los datos locales:

```powershell
docker compose down -v
```

Usarlo solamente cuando la informaciÃ³n local pueda descartarse.

## CÃ³mo continuar el desarrollo

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
7. Integrar `develop` en `main` solamente cuando la versiÃ³n estÃ© estable y demostrable.

Reglas adicionales: [CONTRIBUTING.md](CONTRIBUTING.md) y [docs/GIT_WORKFLOW.md](docs/GIT_WORKFLOW.md).

## GestiÃ³n del proyecto

- CÃ³digo: [repositorio de GitHub](https://github.com/No-Country-simulation/G10-ONE-equipo-14)
- Backlog: [proyecto CommunityLab en Jira](https://g10-latam-equipo14.atlassian.net/jira/software/projects/COMLAB/boards/1)
- DocumentaciÃ³n funcional: carpeta [`docs`](docs)
- Documento base del MVP: [docs/CommunityLab_MVP.pdf](docs/CommunityLab_MVP.pdf)
- Guion reproducible para grabar la demo: [docs/GUION_GRABACION_DEMO_REPRODUCIBLE.md](docs/GUION_GRABACION_DEMO_REPRODUCIBLE.md)
- Roadmap y proceso por etapas: [docs/ROADMAP_ETAPAS.md](docs/ROADMAP_ETAPAS.md)
- Guion de demo y cierre: [docs/DEMO_GUIDE.md](docs/DEMO_GUIDE.md)
- Prueba funcional paso a paso: [docs/sets_pruebas/GUIA_PRUEBA_FUNCIONAL.md](docs/sets_pruebas/GUIA_PRUEBA_FUNCIONAL.md)
- Manual de usuario: [docs/MANUAL_USUARIO.md](docs/MANUAL_USUARIO.md)
- Evidencias visuales: [docs/evidence](docs/evidence)
- Entregable tÃ©cnico E1â€“E8: [docs/ENTREGABLE_IMPLEMENTACION_E1_E8.md](docs/ENTREGABLE_IMPLEMENTACION_E1_E8.md)
- Acta de cierre y continuidad: [docs/CIERRE_ETAPA_2026-10-17.md](docs/CIERRE_ETAPA_2026-10-17.md)
- Inventario auditado y brechas pendientes: [docs/INVENTARIO_PROYECTO.md](docs/INVENTARIO_PROYECTO.md)

Antes de empezar una tarea, revisar el backlog para evitar duplicar trabajo y mantener el ticket relacionado actualizado.

## Seguridad

- Nunca subir `.env`, credenciales, claves API ni archivos de configuraciÃ³n de OCI.
- Utilizar credenciales diferentes para producciÃ³n.
- Mantener PostgreSQL sin publicar al host salvo que una tarea local lo requiera.
- Revisar cualquier dato de comunidad antes de utilizarlo con proveedores externos de IA.

## Licencia

El repositorio todavÃ­a no contiene un archivo de licencia. Antes de distribuirlo fuera del equipo, definir y agregar la licencia correspondiente.
