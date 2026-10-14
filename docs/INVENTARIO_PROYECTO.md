# Inventario integral de CommunityLab

Fecha de corte: 14 de octubre de 2026.

Este documento contrasta el alcance original del hackathon, el MVP técnico, el código de `main`, las pruebas, el despliegue público y la trazabilidad en GitHub/Jira. Su finalidad es evitar que una épica o ticket cerrado oculte una funcionalidad todavía parcial.

## 1. Resumen ejecutivo

CommunityLab cuenta con una base funcional y reproducible: ingesta JSON/CSV, PostgreSQL, deduplicación, idempotencia, análisis determinístico, oportunidades, activos LinkedIn/FAQ, curaduría por API, publicación mediante adaptador, pruebas y despliegue público en Render.

Sin embargo, el MVP no cumple todavía todos los requisitos obligatorios originales. Las brechas principales son:

1. El pipeline activo usa `MockAnalysisProvider`; no existe conexión a un LLM real.
2. Render usa almacenamiento local efímero; la publicación activa no llega a OCI Object Storage.
3. El layout completo `raw/analyzed/generated/approved/manifests` no está implementado y el manifest no se guarda como objeto.
4. Streamlit no ofrece cola persistente, fuentes visibles completas ni acción/confirmación de publicación.
5. Las reglas funcionales de recurrencia, consentimiento y alertas internas no están completas.

Por eso, el estado global correcto es **MVP demostrable, pero parcialmente completo frente al enunciado original**.

### Secuencia acordada de implementación

El equipo decidió completar primero el funcionamiento de la aplicación y abordar OCI únicamente después de superar el **gate funcional** definido en este inventario.

Esta decisión cambia el orden, no el alcance final:

- **OCI Object Storage continúa siendo obligatorio** para la entrega final del MVP según `Detalle_proyecto.pdf`.
- **OCI Compute es opcional**; la aplicación puede continuar desplegada en Render.
- No se configurarán credenciales, publicación ni pruebas OCI mientras el gate funcional esté abierto.
- La fase OCI comienza sólo cuando el flujo local/Render con LLM, reglas, activos y curaduría esté aprobado.

## 2. Evidencia de verificación

- Rama revisada: `main`, commit `95c2e11`.
- Ejecución local: API, PostgreSQL y dashboard iniciaron correctamente con Docker Compose.
- Pruebas en `main`: **94 aprobadas**, con 1 advertencia de deprecación.
- Health local y público: API y PostgreSQL en estado `ok`.
- Pull request pendiente: [#125](https://github.com/No-Country-simulation/G10-ONE-equipo-14/pull/125), CI verde, todavía sin integrar.
- GitHub: las épicas E2-E8 están cerradas.
- Jira: existen épicas y tareas reabiertas, en desarrollo, en revisión o canceladas que contradicen ese cierre.

## 3. Inventario por etapa

| Etapa | Estado auditado | Implementado | Falta o requiere corrección |
| --- | --- | --- | --- |
| E1 - Base técnica | Completa para MVP | FastAPI, Pydantic, PostgreSQL, Docker Compose, Streamlit, CI y dataset | Añadir controles de calidad adicionales al CI |
| E2 - Persistencia | Completa | Tablas, relaciones, índices, migraciones, downgrade y triggers `updated_at` | Actualizar documentación antigua que aún menciona respuestas 501 |
| E3 - Pipeline de IA | Parcial | Interfaz de proveedor, análisis determinístico, persistencia, reintento, PII y routing | Proveedor LLM real, configuración segura y validación real de salida; decidir si se incorpora LangGraph |
| E4 - Contenido | Parcial | LinkedIn/FAQ determinísticos, prompts versionados y trazabilidad | Integrar PR #125; hoy no hay copywriting generado por LLM ni consentimiento del autor |
| E5 - Curaduría | Parcial | API de listado, edición, aprobación/rechazo y auditoría; botones básicos en Streamlit | Cola global persistente, carga por `run_id`, fuentes visibles, comentarios/revisor editables, manejo de errores y estados válidos |
| E6 - OCI y manifests | Parcial | Adapter OCI/local, paquete JSON, SHA-256, ETag y registro de manifest en PostgreSQL | OCI activo, layout obligatorio completo, upload del manifest y confirmación visual en Streamlit |
| E7 - Cierre MVP | Parcial | 94 pruebas, tres recorridos E2E básicos, request ID, README y demo | Pruebas con LLM/OCI reales, logs JSON, métricas de calidad/tiempo y evidencias visuales E1-E6 |
| E8 - Despliegue | Parcial operativo | Render HTTPS, PostgreSQL y health público | Persistencia duradera, backup ejecutado/restaurado, almacenamiento OCI activo y plan por vencimiento de la base Free |

## 4. Lista maestra de brechas

Los identificadores `INV-*` son estables y deben reutilizarse en GitHub y Jira.

### Fase A - gate funcional obligatorio antes de OCI

- [x] **INV-001 - Integrar un LLM real.** Proveedor Gemini configurable, mock para pruebas, salida estructurada, evidencia exacta y registro de `model`/`prompt_version`. Recorrido real: 20/20 análisis con `gemini-3.1-flash-lite`, sin errores, y fallback comprobado. Evidencia: `docs/evidence/INV-001-gemini-validation/README.md`. GitHub #133 / Jira COMLAB-85.
- [x] **INV-006 - Integrar y revisar PR #125.** Validaciones incorporadas mediante PR #125 y liberadas a `main` mediante PR #132, con CI verde. Relacionado con COMLAB-40, COMLAB-41 y COMLAB-62.
- [x] **INV-007 - Cola persistente de curaduría.** Streamlit consulta `GET /assets?status=PENDING_REVIEW`, permite actualizar la cola y retira los activos decididos. Validado con 110 pruebas y comprobación visual local. GitHub #136 / Jira COMLAB-86.
- [x] **INV-008 - Consulta visual por `run_id`.** El dashboard valida el UUID, consulta `GET /runs/{run_id}` y recupera resumen, análisis, oportunidades y activos, con manejo visible de ejecución inexistente o en proceso. GitHub #141 / Jira COMLAB-87.
- [ ] **INV-009 - Evidencia y fuentes visibles.** Mostrar en cada análisis/activo los excerpts y `source_interaction_ids`. Cierre: el curador puede justificar cada afirmación sin inspeccionar JSON bruto.
- [ ] **INV-010 - Máquina de estados de activos.** Impedir transiciones inválidas y publicaciones duplicadas; definir comportamiento de reabrir/rechazar. Cierre: reglas centralizadas y pruebas de cada transición.
- [ ] **INV-011 - Consentimiento y anonimización.** Incorporar `opt-out`/autorización de cita y redacción de PII; el detector actual sólo bloquea correos y teléfonos. Cierre: casos de nombre, correo, teléfono y autor sin consentimiento.
- [ ] **INV-012 - FAQ por recurrencia.** Implementar agregación de preguntas y umbral `N`; actualmente la decisión se toma interacción por interacción. Cierre: pregunta aislada no genera FAQ y preguntas recurrentes sí.
- [ ] **INV-013 - Alertas internas.** El sentimiento negativo/frustración debe generar una alerta interna y nunca contenido público. Cierre: ruta y visualización separadas, con prueba de no publicación.
- [ ] **INV-014 - Resumen funcional completo.** Mostrar sentimiento predominante, temas principales y tiempo de procesamiento, además de cantidades.
- [ ] **INV-016 - Manejo de errores del dashboard.** Capturar errores de editar/aprobar/rechazar y presentar mensajes sin romper la ejecución Streamlit.

El gate funcional queda aprobado cuando INV-001 y todos los puntos INV-006 a INV-014 e INV-016 están cerrados, las pruebas están verdes y los tres recorridos se pueden demostrar sin OCI usando almacenamiento local controlado.

### Fase B - integración OCI obligatoria después del gate funcional

- [ ] **INV-002 - Activar OCI Object Storage.** Configurar el entorno de demostración para que un activo aprobado se guarde en el bucket OCI sin versionar secretos. Cierre: objeto comprobable en OCI con recibo, ETag y SHA-256.
- [ ] **INV-003 - Completar el layout del bucket.** Guardar objetos bajo `raw/`, `analyzed/`, `generated/`, `approved/` y `manifests/` con fecha, comunidad y `run_id`. Cierre: prueba de integración que valide todas las keys.
- [ ] **INV-004 - Persistir el manifest como objeto.** Además del registro PostgreSQL, cargar `manifest.json` con `schema_version`, `run_id`, object keys, content types, SHA-256 y fecha. Cierre: lectura y verificación del manifest desde OCI.
- [ ] **INV-005 - Completar publicación en Streamlit.** Agregar acción Publicar sólo para aprobados y mostrar bucket, object key, ETag y checksum. Cierre: demostración visual de aprobación a objeto OCI.

### Fase C - operación, calidad y coherencia

- [ ] **INV-015 - Observabilidad estructurada.** Emitir logs JSON sin texto sensible y métricas de duración, errores, reintentos y almacenamiento.
- [ ] **INV-017 - Protección de la API pública.** Definir autenticación mínima o limitar las operaciones mutables del entorno público; documentar CORS y rate limiting.
- [ ] **INV-018 - Respaldo y restauración verificados.** Ejecutar backup y restore de PostgreSQL; el script existente no prueba restauración y Render Free expira.
- [ ] **INV-019 - Endurecer CI.** Añadir lint/format, análisis de tipos o estático, auditoría de dependencias, prueba del dashboard y smoke test desplegado.
- [ ] **INV-020 - Corregir documentación obsoleta.** Actualizar `docs/INTERACTION_TABLE.md`, `docs/audits/CL-001_BASELINE_AUDIT.md` y la sección “Próxima etapa” del roadmap.
- [ ] **INV-021 - Completar evidencias visuales.** Crear capturas para E1-E6 y una evidencia final que muestre curaduría y publicación real.

### Fase D - mejoras posteriores al MVP

- [ ] **INV-022 - Entrada automática.** Evaluar webhook/n8n/Discord/Slack sólo después de cerrar P0 y P1.
- [ ] **INV-023 - Procesamiento asíncrono.** Medir lotes de 500 elementos; agregar worker/cola sólo si se supera el objetivo de 30 segundos.
- [ ] **INV-024 - Métricas de evaluación.** Medir validez de salida, grounding y precisión de oportunidades con una muestra humana.
- [ ] **INV-025 - Canales adicionales.** X/Twitter, newsletter, highlights e informes de sentimiento quedan como alcance posterior.

## 5. Inconsistencias de seguimiento

### GitHub

- Las épicas E2-E8 figuran cerradas, aunque las brechas P0/P1 anteriores permanecen.
- El PR #125 está abierto y con CI verde; sus cambios no forman parte de `main`.
- No deben cerrarse los nuevos puntos por la existencia de clases o mocks: el criterio es un recorrido verificable.

### Jira

Estado observado el 14 de octubre de 2026:

- COMLAB-14 (Curaduría) y COMLAB-16 (Cierre MVP): **En Desarrollo**.
- COMLAB-40, COMLAB-41 y COMLAB-62: **En revisión** y vinculados al PR #125.
- COMLAB-43, COMLAB-44, COMLAB-45, COMLAB-49, COMLAB-50, COMLAB-51 y COMLAB-64: **Reabierto**.
- COMLAB-52, COMLAB-55, COMLAB-56, COMLAB-57 y COMLAB-58: **Cancelado**, aunque cubren publicación/manifest/OCI solicitados por el alcance original.
- COMLAB-63 y COMLAB-65: **En Desarrollo**.

Antes de declarar terminado el MVP se debe reconciliar Jira con esta lista y evitar que una épica “Finalizada” contenga obligaciones canceladas o reabiertas.

## 6. Orden recomendado de cierre

1. Revisar y resolver PR #125.
2. Crear una épica de cierre de brechas y tickets separados para INV-001 a INV-021, sin asignarlos inicialmente.
3. Completar la Fase A: LLM real, reglas, dos activos y curaduría persistente en Streamlit.
4. Ejecutar y aprobar los tres recorridos funcionales con almacenamiento local controlado.
5. Recién entonces completar la Fase B: OCI Object Storage, package, manifest, layout y confirmación visual.
6. Repetir los tres recorridos con OCI activo.
7. Completar seguridad, observabilidad, backup y documentación.
8. Capturar evidencias finales, reconciliar Jira/GitHub y cerrar la épica.

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
