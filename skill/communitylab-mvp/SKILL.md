---
name: communitylab-mvp
description: Diseña, implementa, revisa y documenta el MVP de CommunityLab en este repositorio. Usar para cambios de API, ingesta, IA, reglas de contenido, curaduría, PostgreSQL, OCI Object Storage, Streamlit, pruebas o arquitectura del proyecto; no usar para proyectos ajenos a CommunityLab.
---

# CommunityLab MVP

Trabaja sobre CommunityLab como un producto asistido por IA con curaduría humana. Mantén alineados el código, los contratos, las pruebas y la documentación sin presentar funcionalidad planificada como ya implementada.

## Antes de actuar

1. Lee los archivos del área solicitada y sus pruebas antes de proponer o editar código.
2. Si la tarea depende del alcance, la arquitectura, los contratos o el estado de implementación, lee [references/project-context.md](references/project-context.md).
3. Clasifica cada requisito relevante como uno de estos casos:
   - obligatorio por el desafío;
   - decisión del MVP de este equipo;
   - implementado actualmente;
   - planificado o fuera de alcance.
4. Si las fuentes discrepan, señala la diferencia. No adaptes silenciosamente un contrato histórico al contrato vigente.

## Principios del producto

- El recorrido objetivo es: ingerir JSON o CSV, validar y deduplicar, analizar, detectar oportunidades, generar borradores, someterlos a revisión humana y persistir los paquetes aprobados en OCI Object Storage.
- El MVP del equipo genera solamente `LINKEDIN` y `FAQ`. Newsletter, X, alertas, highlights, conectores productivos, RAG, embeddings, fine-tuning, publicación automática y OCI Compute no forman parte del recorrido mínimo actual salvo que una tarea amplíe el alcance de forma explícita.
- Nunca agregues publicación automática. Los estados de activo son `DRAFT`, `PENDING_REVIEW`, `APPROVED` y `REJECTED`; `PUBLISHED` queda fuera del MVP.
- PostgreSQL es la fuente de estado operativo y auditoría. OCI Object Storage conserva objetos y paquetes; no sustituye a PostgreSQL.
- La lógica determinística controla validaciones, deduplicación, umbrales, routing, estados e idempotencia. El LLM interpreta y redacta, pero no decide por sí solo estados ni publicación.
- Todo activo debe poder rastrearse a interacciones y evidencia de origen. No inventes hechos ni completes evidencia ausente con conocimiento general.
- Contenido con PII, afirmaciones sensibles, falta de evidencia o confianza menor que `0.70` debe bloquearse o marcarse para revisión. La oportunidad de LinkedIn usa inicialmente relevancia mayor o igual que `0.75`.
- Mantén los secretos fuera del repositorio. Usa configuración por entorno y documenta nuevas variables en `.env.example` cuando corresponda.

## Contratos y compatibilidad

- Trata `app/schemas/v1/` y las pruebas de contrato como la verdad del contrato vigente.
- Conserva `schema_version` y los contratos versionados en todas las fronteras públicas.
- Para el procesamiento JSON actual, usa `POST /api/v1/process`, el encabezado obligatorio `Idempotency-Key` y `ProcessRequest`. Para CSV, usa `POST /api/v1/process/csv` con los campos de formulario definidos en el endpoint.
- No copies el ejemplo histórico con `origen_comunidad`, `periodo_referencia` y `activos_distribucion_generados` como si fuera el contrato vigente. Si se necesita compatibilidad con ese formato, diseña un adaptador explícito y prúbalo.
- La deduplicación por fingerprint y por `external_id` está acotada por organización y comunidad. Preserva las restricciones de base de datos como defensa ante concurrencia.
- Una misma `Idempotency-Key` con el mismo payload debe reproducir la respuesta original; reutilizarla con otro payload debe producir conflicto.
- Los cambios incompatibles requieren una nueva versión del contrato o una decisión explícita de migración. No rompas v1 de manera incidental.

## IA y generación de contenido

- Define salidas estructuradas y valídalas con Pydantic. Permite como máximo el número de reintentos correctivos configurado y termina con un fallback controlado.
- Mantén separados análisis, routing determinístico, generación y quality gate.
- Registra `model` y `prompt_version` en el análisis. Evita incluir texto sensible o credenciales en logs.
- Usa prompts distintos por tipo de activo: LinkedIn inspirador y profesional; FAQ claro, didáctico y técnicamente verificable.
- Usa few-shot cuando ejemplos representativos mejoren de forma demostrable la consistencia. No lo agregues mecánicamente a todos los prompts.
- Una FAQ necesita validación técnica antes de publicarse. Un testimonio debe permanecer anonimizado hasta contar con autorización para identificar o citar al autor.

## Forma de implementar

- Haz el cambio más pequeño que complete la tarea y respeta la separación existente entre API, schemas, dominio, servicios, persistencia y dashboard.
- No agregues Redis, workers, n8n, conectores externos ni infraestructura productiva por anticipado. Redis y workers sólo se justifican si las mediciones muestran que el lote no puede resolverse síncronamente dentro del objetivo del MVP.
- Incluye manejo de errores y logging estructurado donde aporten observabilidad real. No impongas docstrings o abstracciones ceremoniales a código trivial.
- Mantén los endpoints de curaduría alineados con los estados del dominio y registra quién editó, aprobó o rechazó cuando se implemente su persistencia.
- Cuando cambie un contrato, una regla o un paso de instalación, actualiza en la misma tarea las pruebas y la documentación afectadas.

## Verificación

- Ejecuta primero las pruebas enfocadas y después `pytest -q` cuando el entorno lo permita.
- Para cambios de base de datos, agrega o modifica una migración de Alembic; no dependas solamente de `Base.metadata.create_all`.
- Para cambios de ingesta, cubre como mínimo entradas válidas, normalización, duplicados del lote, duplicados persistidos y errores por registro.
- Para cambios de IA, prueba schemas, routing, ausencia de evidencia, baja confianza, PII y fallback sin depender de llamadas reales al proveedor en pruebas unitarias.
- Para cambios de curaduría, verifica edición, aprobación, rechazo y la imposibilidad de publicar automáticamente.
- Describe con honestidad las verificaciones omitidas o bloqueadas y la funcionalidad que continúa pendiente.
