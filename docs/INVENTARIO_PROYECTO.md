# Inventario integral de CommunityLab

Fecha de corte: 16 de octubre de 2026.

Este documento contrasta el alcance original del hackathon, el MVP técnico, el código de `main`, las pruebas, el despliegue público y la trazabilidad en GitHub/Jira. Su finalidad es evitar que una épica o ticket cerrado oculte una funcionalidad todavía parcial.

## 1. Resumen ejecutivo

CommunityLab tiene completa la funcionalidad no OCI inventariada: ingesta manual y
webhook, PostgreSQL, deduplicación e idempotencia, Gemini con fallback, privacidad,
oportunidades, activos LinkedIn/FAQ, curaduría, alertas, procesamiento asíncrono,
evaluación de calidad, observabilidad, backup, CI, evidencias y despliegue público
en Render.

El único bloque pendiente del alcance obligatorio es la integración OCI final:
activar el bucket, completar su layout, persistir el manifest como objeto y
mostrar la confirmación de publicación desde Streamlit. Corresponde exactamente a
INV-002 a INV-005 y está proyectado en issues abiertos y sin asignar.

Por eso, el estado global correcto es **desarrollo funcional no OCI completo;
despliegue final con OCI pendiente**.

### Secuencia acordada de implementación

El equipo decidió completar primero el funcionamiento de la aplicación y abordar OCI únicamente después de superar el **gate funcional** definido en este inventario.

Esta decisión cambia el orden, no el alcance final:

- **OCI Object Storage continúa siendo obligatorio** para la entrega final del MVP según `Detalle_proyecto.pdf`.
- **OCI Compute es opcional**; la aplicación puede continuar desplegada en Render.
- El gate funcional está aprobado; no quedan brechas no OCI abiertas.
- La próxima fase permitida es INV-002 a INV-005 cuando el equipo retome el
  despliegue final y disponga de credenciales/permisos OCI.

## 2. Evidencia de verificación

- Rama revisada: `main`, commit `b9f4db6` antes de esta auditoría de cierre.
- Pruebas locales al cierre de INV-024: **144 aprobadas**, con 1 advertencia de deprecación.
- CI de `main`: ejecución [38778356140](https://github.com/No-Country-simulation/G10-ONE-equipo-14/actions/runs/38778356140) verde para quality, pruebas y Terraform.
- GitHub: no había PR abierto; INV-001 e INV-006 a INV-025 estaban cerrados.
- Jira: COMLAB-103 y COMLAB-104 estaban Finalizados y sin asignar; los cuatro
  pendientes OCI quedaron creados como COMLAB-105 a COMLAB-108, estado Por hacer
  y sin asignar.
- Los únicos archivos locales ajenos al cierre son las copias no versionadas
  `docs/Detalle_proyecto.pdf` y `docs/Prueba.csv`; se conservaron sin modificar.

## 3. Inventario por etapa

| Etapa | Estado auditado | Implementado | Falta o requiere corrección |
| --- | --- | --- | --- |
| E1 - Base técnica | Completa | FastAPI, Pydantic, PostgreSQL, Docker Compose, Streamlit, CI y datasets | Sin brecha no OCI abierta |
| E2 - Persistencia | Completa | Tablas, relaciones, índices, migraciones, downgrade, triggers y cola durable | Sin brecha abierta |
| E3 - Pipeline de IA | Completa | Gemini configurable, fallback mock, salida validada, grounding, PII, reintento y routing | Sin brecha abierta |
| E4 - Contenido | Completa | LinkedIn/FAQ, prompts versionados, trazabilidad, recurrencia y consentimiento | Sin brecha abierta |
| E5 - Curaduría | Completa | Cola persistente, consulta por run, fuentes, edición, estados, aprobación/rechazo y errores visuales | Sin brecha abierta |
| E6 - OCI y manifests | Parcial | Adapter OCI/local, paquete JSON, SHA-256, ETag y registro de manifest en PostgreSQL | OCI activo, layout obligatorio completo, upload del manifest y confirmación visual en Streamlit |
| E7 - Cierre MVP | Completa salvo OCI | 144 pruebas, E2E, logs JSON, métricas, benchmark, backup y evidencias visuales | Repetir validación final con OCI activo |
| E8 - Despliegue | Operativa en Render; OCI pendiente | Render HTTPS, PostgreSQL, health, protección pública y backup/restauración | Activar almacenamiento OCI mediante INV-002 a INV-005 |

## 4. Lista maestra de brechas

Los identificadores `INV-*` son estables y deben reutilizarse en GitHub y Jira.

### Fase A - gate funcional obligatorio antes de OCI

- [x] **INV-001 - Integrar un LLM real.** Proveedor Gemini configurable, mock para pruebas, salida estructurada, evidencia exacta y registro de `model`/`prompt_version`. Recorrido real: 20/20 análisis con `gemini-3.1-flash-lite`, sin errores, y fallback comprobado. Evidencia: `docs/evidence/INV-001-gemini-validation/README.md`. GitHub #133 / Jira COMLAB-85.
- [x] **INV-006 - Integrar y revisar PR #125.** Validaciones incorporadas mediante PR #125 y liberadas a `main` mediante PR #132, con CI verde. Relacionado con COMLAB-40, COMLAB-41 y COMLAB-62.
- [x] **INV-007 - Cola persistente de curaduría.** Streamlit consulta `GET /assets?status=PENDING_REVIEW`, permite actualizar la cola y retira los activos decididos. Validado con 110 pruebas y comprobación visual local. GitHub #136 / Jira COMLAB-86.
- [x] **INV-008 - Consulta visual por `run_id`.** El dashboard valida el UUID, consulta `GET /runs/{run_id}` y recupera resumen, análisis, oportunidades y activos, con manejo visible de ejecución inexistente o en proceso. GitHub #141 / Jira COMLAB-87.
- [x] **INV-009 - Evidencia y fuentes visibles.** Análisis y activos muestran los excerpts y `source_interaction_ids`; la API conserva las fuentes al listar, editar y decidir. Validado con pruebas y recorrido visual local. GitHub #144 / Jira COMLAB-88.
- [x] **INV-010 - Máquina de estados de activos.** Las decisiones sólo permiten `PENDING_REVIEW -> APPROVED|REJECTED`; un rechazado se reabre únicamente al editarlo y un aprobado es inmutable. La publicación es idempotente, bloquea la fila del activo y conserva un único manifest por activo. Validado con 115 pruebas. GitHub #147 / Jira COMLAB-89.
- [x] **INV-011 - Consentimiento y anonimización.** JSON y CSV aceptan `publication_consent` y `opt_out`; correo y teléfono se redactan antes de persistir/analizar, el nombre se reemplaza por `[PERSON]` sin consentimiento y el opt-out bloquea activos públicos. GitHub #150 / Jira COMLAB-90.
- [x] **INV-012 - FAQ por recurrencia.** El pipeline agrupa preguntas por tema dentro de la ejecución y genera una sola FAQ al alcanzar `FAQ_RECURRENCE_THRESHOLD` (2 por defecto), conservando todas las fuentes. Preguntas aisladas y mensajes que no son preguntas no generan FAQ. GitHub #153 / Jira COMLAB-91.
- [x] **INV-013 - Alertas internas.** El sentimiento negativo/frustración crea una alerta persistente `OPEN`, bloquea la oportunidad pública y nunca genera activos. Las alertas se consultan en `GET /api/v1/alerts` y se muestran en una pestaña separada del dashboard. GitHub #156 / Jira COMLAB-92.
- [x] **INV-014 - Resumen funcional completo.** La respuesta y el dashboard muestran sentimiento predominante, los tres temas más frecuentes y tiempo de procesamiento en milisegundos, además de cantidades. La respuesta idempotente conserva los mismos valores. GitHub #159 / Jira COMLAB-93.
- [x] **INV-016 - Manejo de errores del dashboard.** Carga, consulta, alertas, cola, edición, aprobación y rechazo capturan errores de red/HTTP y muestran el `detail` útil de FastAPI sin exponer HTML ni interrumpir Streamlit. GitHub #162 / Jira COMLAB-94.

El gate funcional queda aprobado cuando INV-001 y todos los puntos INV-006 a INV-014 e INV-016 están cerrados, las pruebas están verdes y los tres recorridos se pueden demostrar sin OCI usando almacenamiento local controlado.

### Fase B - integración OCI obligatoria después del gate funcional

- [ ] **INV-002 - Activar OCI Object Storage.** Configurar el entorno de demostración para que un activo aprobado se guarde en el bucket OCI sin versionar secretos. Cierre: objeto comprobable en OCI con recibo, ETag y SHA-256. GitHub #195 / Jira COMLAB-105 (Por hacer, sin asignar).
- [ ] **INV-003 - Completar el layout del bucket.** Guardar objetos bajo `raw/`, `analyzed/`, `generated/`, `approved/` y `manifests/` con fecha, comunidad y `run_id`. Cierre: prueba de integración que valide todas las keys. GitHub #196 / Jira COMLAB-106 (Por hacer, sin asignar).
- [ ] **INV-004 - Persistir el manifest como objeto.** Además del registro PostgreSQL, cargar `manifest.json` con `schema_version`, `run_id`, object keys, content types, SHA-256 y fecha. Cierre: lectura y verificación del manifest desde OCI. GitHub #197 / Jira COMLAB-107 (Por hacer, sin asignar).
- [ ] **INV-005 - Completar publicación en Streamlit.** Agregar acción Publicar sólo para aprobados y mostrar bucket, object key, ETag y checksum. Cierre: demostración visual de aprobación a objeto OCI. GitHub #198 / Jira COMLAB-108 (Por hacer, sin asignar).

### Fase C - operación, calidad y coherencia

- [x] **INV-015 - Observabilidad estructurada.** Solicitudes, análisis y almacenamiento emiten eventos JSON con duración, estado, reintentos, tipo de error y bytes, sin registrar textos de interacción ni mensajes de excepción. GitHub #165 / Jira COMLAB-95.
- [x] **INV-017 - Protección de la API pública.** Las mutaciones tienen interruptor por entorno, clave API opcional y rate limiting; la demo pública queda en modo sólo lectura y CORS está documentado. Evidencia: `docs/evidence/INV-017-api-protection/README.md`.
- [x] **INV-018 - Respaldo y restauración verificados.** El backup genera un dump custom validado y la restauración se prueba en una base temporal, comparando revisión Alembic, tablas y conteos antes de eliminarla. Evidencia: `docs/evidence/INV-018-backup-restore/README.md`.
- [x] **INV-019 - Endurecer CI.** CI ejecuta Ruff, formato incremental, auditoría de dependencias, compilación del dashboard, pruebas/migraciones y smoke tests de API/dashboard en `main`. Evidencia: `docs/evidence/INV-019-ci-hardening/README.md`.
- [x] **INV-020 - Corregir documentación obsoleta.** `INTERACTION_TABLE` refleja la consulta real de runs, CL-001 se identifica como auditoría histórica con matriz de resolución y el roadmap muestra el estado y orden vigentes. Evidencia: `docs/evidence/INV-020-documentation/README.md`.
- [x] **INV-021 - Completar evidencias visuales.** Se versionaron capturas reales de E1-E6: health, contrato OpenAPI, análisis Gemini con fuentes, oportunidades, cola persistente y recibo de publicación local con object key/ETag/SHA-256. Evidencia: `docs/evidence/INV-021-visual-evidence/README.md`.

### Fase D - mejoras posteriores al MVP

- [x] **INV-022 - Entrada automática.** Webhook neutral protegido e idempotente que integra n8n/Discord/Slack con el pipeline existente; incluye contrato, mapeos, reintentos y pruebas sin credenciales externas. Evidencia: `docs/evidence/INV-022-webhook-input/README.md`.
- [x] **INV-023 - Procesamiento asíncrono.** Tres mediciones síncronas de 500 elementos dieron 15,105 s, 64,337 s y 47,762 s; al no cumplir de forma estable el objetivo de 30 segundos se agregó una cola durable PostgreSQL, endpoint consultable y worker separado. La prueba final encoló 500 elementos en 0,062 s y terminó en 19,841 s con proveedor mock. Evidencia: `docs/evidence/INV-023-async-benchmark/README.md`. GitHub #186 / Jira COMLAB-102.
- [x] **INV-024 - Métricas de evaluación.** Muestra humana versionada de 20 casos, guía de anotación y evaluación reproducible: 100% de validez, 100% de grounding, 100% de precisión y 90,91% de recall en la línea base determinística. Se documentan un falso negativo y los límites de tamaño y revisor único. Evidencia: `docs/evidence/INV-024-quality-evaluation/README.md`. GitHub #189 / Jira COMLAB-103.
- [x] **INV-025 - Canales adicionales.** Se decidió y documentó el alcance posterior: highlights semanales, informe interno de sentimiento, newsletter y X/Twitter, en ese orden recomendado. Cada incremento tiene contrato, límites de privacidad, criterios de aceptación y gate de inicio; no se declara implementado. Evidencia: `docs/evidence/INV-025-channel-roadmap/README.md`. GitHub #192 / Jira COMLAB-104.

## 5. Seguimiento reconciliado

- Los tickets históricos no se usan para afirmar cierre de una brecha nueva; cada
  INV tiene evidencia específica y, cuando corresponde, GitHub/Jira enlazados.
- Los cuatro criterios OCI que seguían abiertos tienen ahora seguimiento propio:
  GitHub #195–#198 y Jira COMLAB-105–COMLAB-108.
- No hay PR pendiente al inicio de esta auditoría de cierre.
- Los puntos no OCI INV-001 e INV-006–INV-025 están marcados `[x]`; no se encontró
  otro checkbox abierto fuera de INV-002–INV-005.

## 6. Próximo orden de cierre

1. Retomar INV-002 cuando exista ventana de despliegue y acceso OCI válido.
2. Completar INV-003 e INV-004 sobre el mismo entorno y bucket.
3. Completar INV-005 y capturar la confirmación visual real.
4. Repetir los tres recorridos finales con OCI activo.
5. Ejecutar nuevamente suite, smoke tests, backup y auditoría de seguridad.
6. Cerrar los cuatro pares GitHub/Jira y declarar completa la entrega con OCI.

## 7. Regla para marcar un punto

Un checkbox sólo pasa a `[x]` cuando existen simultáneamente:

1. Código integrado en `develop` y posteriormente en `main` cuando corresponda.
2. Pruebas verdes proporcionales al riesgo.
3. Demostración local o pública reproducible.
4. Evidencia técnica o visual versionada.
5. Issue GitHub y ticket Jira enlazados y con el mismo estado.

## 8. Trazabilidad de esta auditoría

- GitHub: [#126](https://github.com/No-Country-simulation/G10-ONE-equipo-14/issues/126)
- Jira: [COMLAB-83](https://g10-latam-equipo14.atlassian.net/browse/COMLAB-83)
- Ajuste de secuencia: [GitHub #129](https://github.com/No-Country-simulation/G10-ONE-equipo-14/issues/129) / [COMLAB-84](https://g10-latam-equipo14.atlassian.net/browse/COMLAB-84).
- Documentos fuente canónicos: `docs/CommunityLab_MVP.pdf` y `docs/PROYECTO-communityLAB-Motot Inteligente de Transformación y Distribución para Comunidades Digitales.pdf`. La copia local `Detalle_proyecto.pdf` fue revisada y tiene exactamente el mismo SHA-256 que el segundo documento, por lo que no se versiona dos veces.
