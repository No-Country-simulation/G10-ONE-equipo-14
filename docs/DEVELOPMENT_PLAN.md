# Plan de desarrollo inicial - CommunityLab

Este documento organiza el trabajo del equipo sin duplicar la aplicación existente. Cada ticket se implementa en una rama corta creada desde `develop` y se integra mediante pull request.

## Estructura oficial

- `app/`: API FastAPI, contratos, dominio, servicios y persistencia.
- `dashboard/`: interfaz Streamlit.
- `alembic/versions/`: cambios versionados de base de datos.
- `tests/`: pruebas unitarias, de contrato e integración.
- `docs/`: decisiones, contratos y guías del proyecto.
- `skill/communitylab-mvp/`: instrucciones especializadas para asistentes de desarrollo.

Las carpetas vacías `backend/` y `frontend/` no se usarán mientras el equipo no apruebe una migración completa de estructura. No se crearán copias paralelas de `app/` o `dashboard/`.

## Flujo Git

- `main`: versión estable y demostrable.
- `develop`: integración del equipo.
- `feature/<ticket>-<descripcion>`: funcionalidad nueva.
- `fix/<ticket>-<descripcion>`: corrección.
- `docs/<ticket>-<descripcion>`: documentación.

Cada rama parte de `develop`. Los pull requests normales apuntan a `develop`; el equipo promueve `develop` a `main` al cerrar una etapa estable.

Antes de integrar:

1. Actualizar la rama con `develop`.
2. Ejecutar las pruebas relacionadas y, cuando sea posible, `pytest -q`.
3. Confirmar que no haya secretos ni archivos `.env` versionados.
4. Documentar cambios de contrato, migraciones y verificaciones pendientes.
5. Obtener al menos una revisión de otro integrante.

## Etapa 0 - Alinear la base existente

### [CL-001 - Auditar el código actual](https://github.com/No-Country-simulation/G10-ONE-equipo-14/issues/35)

**Objetivo:** determinar qué partes del repositorio se conservan, corrigen o reemplazan antes de asignar nuevas funcionalidades.

**Alcance:**

- Revisar `app/`, `dashboard/`, migraciones y pruebas.
- Comparar el comportamiento existente con los schemas v1 y el alcance del MVP.
- Registrar defectos, deuda técnica y componentes incompletos.
- No reescribir código durante esta auditoría.

**Criterio de aceptación:** inventario aprobado por el equipo con decisiones de conservar, corregir o retirar por componente.

### [CL-002 - Confirmar el modelo de datos](https://github.com/No-Country-simulation/G10-ONE-equipo-14/issues/36)

**Objetivo:** revisar las tablas `interactions` y `runs` existentes y diseñar las entidades todavía necesarias.

**Alcance:**

- Validar claves, restricciones, índices y relaciones actuales.
- Diseñar `analyses`, `opportunities`, `assets`, `approvals` y manifests si se confirma su persistencia.
- Definir qué reglas pertenecen a PostgreSQL y cuáles al dominio Python.
- Proponer nuevas migraciones sin modificar migraciones ya compartidas.

**Criterio de aceptación:** diagrama y decisión de modelo aprobados antes de crear tablas adicionales.

## Etapa 1 - Esqueleto visual y base técnica

### [CL-003 - Maquetar la interfaz Streamlit](https://github.com/No-Country-simulation/G10-ONE-equipo-14/issues/37)

**Objetivo:** crear el recorrido visual completo con datos simulados, sin implementar todavía las validaciones funcionales del frontend.

**Pantallas o secciones:**

- Carga JSON/CSV.
- Resumen de ejecución.
- Tabla de análisis y evidencia.
- Lista de oportunidades.
- Tarjetas editables de LinkedIn y FAQ.
- Acciones visuales de guardar, aprobar y rechazar.
- Confirmación visual de almacenamiento OCI.

**Criterio de aceptación:** el recorrido puede demostrarse con fixtures locales y no afirma que una operación se haya persistido o enviado cuando sólo está simulada.

### [CL-004 - Estabilizar la base FastAPI](https://github.com/No-Country-simulation/G10-ONE-equipo-14/issues/38)

**Objetivo:** conservar una API integrable para que los demás integrantes desarrollen por contratos.

**Alcance:**

- Verificar health check, schemas v1 y documentación OpenAPI.
- Mantener endpoints no implementados con respuestas explícitas, sin simular éxito.
- Preparar fixtures y dobles de prueba para el dashboard.
- Documentar variables de entorno en `.env.example`.

**Criterio de aceptación:** API y dashboard levantan con Docker Compose y los contratos acordados están documentados.

### [CL-005 - Diseñar los triggers de PostgreSQL](https://github.com/No-Country-simulation/G10-ONE-equipo-14/issues/39)

**Objetivo:** incorporar solamente disparadores que resuelvan requisitos de integridad o auditoría aprobados.

**Decisiones requeridas antes de implementar:**

- Evento exacto: `INSERT`, `UPDATE` o `DELETE`.
- Tabla afectada y condición de ejecución.
- Información que registra o regla que protege.
- Comportamiento ante error y efecto sobre transacciones.
- Razón para no resolverlo mediante constraints o dominio Python.

**Candidatos a evaluar:**

- Actualización consistente de `updated_at`.
- Auditoría de cambios de estado de activos.
- Historial inmutable de aprobaciones y rechazos.

**Criterio de aceptación:** cada trigger se crea mediante una nueva migración Alembic, incluye downgrade y tiene pruebas de integración en PostgreSQL. No se crean triggers genéricos sin caso de uso aprobado.

## Etapas posteriores

### [CL-006 - Pipeline de IA](https://github.com/No-Country-simulation/G10-ONE-equipo-14/issues/40)

Implementar gateway de LLM, LangGraph, análisis estructurado, routing determinístico y quality gate. Debe mantener evidencia, versionar modelo y prompt, y bloquear contenido sin sustento.

### [CL-007 - Curaduría persistente](https://github.com/No-Country-simulation/G10-ONE-equipo-14/issues/41)

Implementar edición, aprobación y rechazo con auditoría. Ninguna acción puede publicar automáticamente.

### [CL-008 - OCI Object Storage](https://github.com/No-Country-simulation/G10-ONE-equipo-14/issues/42)

Persistir paquetes aprobados y manifests con checksum, ETag y rutas definidas por el MVP dentro de los recursos gratuitos acordados.

### [CL-009 - Demostración integral](https://github.com/No-Country-simulation/G10-ONE-equipo-14/issues/43)

Preparar al menos tres transformaciones reproducibles, incluyendo un caso exitoso, una FAQ y un contenido bloqueado o enviado a revisión.

## Regla para asignar trabajo

Un ticket debe tener una persona responsable, alcance acotado, dependencias, criterio de aceptación y pruebas esperadas. No se inicia una tarea bloqueada por una decisión de arquitectura pendiente. Los cambios de contrato o base de datos deben comunicarse antes de que otros integrantes construyan sobre ellos.
