# CommunityLab

Motor inteligente de transformación y distribución para comunidades digitales, desarrollado por **G10 · Hackathon ONE · Equipo 14**.

CommunityLab recibe interacciones en JSON o CSV, las normaliza, deduplica y guarda en PostgreSQL. El dashboard Streamlit permite realizar una demostración local de la ingesta. El análisis con IA, la curaduría persistente y la publicación en OCI forman parte de las próximas etapas del MVP.

## Estado del proyecto

### Implementado

- API REST con FastAPI y contratos versionados con Pydantic.
- Carga de interacciones JSON y CSV.
- Normalización, fingerprint SHA-256 y deduplicación por comunidad.
- Idempotencia persistida mediante el encabezado `Idempotency-Key`.
- PostgreSQL 16 con migraciones Alembic automáticas.
- Dashboard Streamlit para cargar archivos y visualizar el resultado.
- Health checks de PostgreSQL y API.
- Suite de 27 pruebas y CI en GitHub Actions.
- Datos de demostración en JSON y CSV.

### Pendiente

- `GET /api/v1/runs/{run_id}` con consulta persistida.
- Pipeline de análisis y generación con LLM/LangGraph.
- Persistencia y curaduría de activos LinkedIn/FAQ.
- Aprobación y rechazo de contenido.
- Publicación en OCI Object Storage.
- Prueba integral de la cadena completa del MVP.

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

Las pestañas de análisis, oportunidades y activos indican explícitamente las etapas que todavía están pendientes.

## Endpoints de la API

| Método | Ruta | Estado actual |
| --- | --- | --- |
| `GET` | `/api/v1/health` | Implementado |
| `POST` | `/api/v1/process` | Ingesta JSON implementada |
| `POST` | `/api/v1/process/csv` | Ingesta CSV implementada |
| `GET` | `/api/v1/runs/{run_id}` | Contrato creado; responde 501 |
| `GET` | `/api/v1/assets` | Contrato inicial; devuelve lista vacía |
| `PATCH` | `/api/v1/assets/{asset_id}` | Contrato creado; responde 501 |
| `POST` | `/api/v1/assets/{asset_id}/approve` | Contrato creado; responde 501 |
| `POST` | `/api/v1/assets/{asset_id}/reject` | Contrato creado; responde 501 |

Todas las rutas versionadas usan el prefijo `/api/v1`.

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

Antes de empezar una tarea, revisar el backlog para evitar duplicar trabajo y mantener el ticket relacionado actualizado.

## Seguridad

- Nunca subir `.env`, credenciales, claves API ni archivos de configuración de OCI.
- Utilizar credenciales diferentes para producción.
- Mantener PostgreSQL sin publicar al host salvo que una tarea local lo requiera.
- Revisar cualquier dato de comunidad antes de utilizarlo con proveedores externos de IA.

## Licencia

El repositorio todavía no contiene un archivo de licencia. Antes de distribuirlo fuera del equipo, definir y agregar la licencia correspondiente.
