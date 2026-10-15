# Roadmap de desarrollo por etapas

Este documento define cómo continuará CommunityLab después de la base funcional del MVP. Su objetivo es que cualquier integrante pueda entender el orden del trabajo, localizar los tickets y saber qué evidencia se exige antes de cerrar una etapa.

## Principios de trabajo

1. Cada etapa se representa mediante una épica en Jira y un issue de seguimiento en GitHub.
2. Los tickets se crean inicialmente sin asignar. La asignación ocurre solamente cuando una persona toma el trabajo.
3. Cada ticket de implementación tiene su equivalente o referencia cruzada entre Jira y GitHub.
4. Se crea una rama corta por ticket desde `develop`.
5. Cada ticket se entrega mediante un pull request enfocado.
6. Un pull request debe incluir pruebas, documentación y referencias a Jira/GitHub.
7. Ninguna etapa se cierra sin CI verde, prueba local y evidencias visuales.
8. Las capturas no pueden mostrar credenciales, tokens, archivos `.env` ni datos sensibles.

## Flujo de una etapa

### 1. Refinamiento

- Confirmar alcance, dependencias y criterios de aceptación.
- Revisar Jira y GitHub para evitar tickets duplicados.
- Mantener los tickets sin asignar hasta que alguien los tome.
- Dividir el trabajo para que cada ticket pueda integrarse de forma independiente.

### 2. Desarrollo

Crear una rama desde `develop`:

```powershell
git switch develop
git pull --ff-only origin develop
git switch -c feature/COMLAB-XX-descripcion
```

Durante la implementación:

- No mezclar varias etapas en un mismo PR.
- No modificar migraciones ya compartidas; crear una nueva revisión Alembic.
- Agregar pruebas proporcionales al cambio.
- Mantener los contratos y la documentación actualizados.

### 3. Pull request

Cada PR debe incluir:

- Resumen del cambio.
- Jira y GitHub relacionados.
- Dependencias.
- Pruebas ejecutadas.
- Pasos para probar localmente.
- Capturas cuando exista un cambio visual.

El PR se abre contra `develop`. Cuando una etapa completa está estable, se publica en `main` mediante un PR de integración.

### 4. Validación

Antes de cerrar un ticket:

- CI de GitHub Actions en verde.
- Suite local aprobada.
- Docker Compose inicia desde una instalación reproducible.
- Criterios de aceptación verificados.
- Capturas y resultados adjuntos.

### 5. Evidencias

Las evidencias versionables se guardan por etapa:

```text
docs/evidence/
├── E2-modelo-persistencia/
├── E3-pipeline-ia/
├── E4-generacion-contenido/
├── E5-curaduria/
├── E6-oci-storage/
├── E7-cierre-mvp/
└── E8-despliegue-oci/
```

Nombres recomendados:

```text
01-diagrama.png
02-swagger.png
03-dashboard.png
04-base-datos.png
05-tests.png
```

Además de versionarlas cuando sea apropiado, las imágenes finales se adjuntan al issue de GitHub, al PR y a la épica/ticket Jira correspondiente.

## Roadmap

### Estado consolidado al 15 de octubre de 2026

| Etapa | Estado actual |
| --- | --- |
| E1 | Completa: base técnica, Docker, PostgreSQL y CI reproducible. |
| E2 | Completa: modelo, migraciones, constraints, triggers y consulta de ejecuciones. |
| E3 | Completa para el alcance funcional: Gemini configurable, fallback mock, persistencia, PII y decisiones. |
| E4 | Completa: activos LinkedIn/FAQ trazables, recurrencia y consentimiento. |
| E5 | Completa para curaduría: cola persistente, edición, decisión, fuentes y manejo de errores. |
| E6 | Parcial por decisión: publicación local funciona; OCI Object Storage (INV-002 a INV-005) queda para el despliegue final. |
| E7 | Funcionalmente completa; resta consolidar todas las capturas y métricas finales del inventario. |
| E8 | Operativa en Render Free; OCI se abordará sólo al finalizar al 100% los puntos de desarrollo. |

La fuente de verdad para brechas abiertas es [`INVENTARIO_PROYECTO.md`](INVENTARIO_PROYECTO.md), no el estado histórico de las épicas.

### E2 — Modelo de datos y persistencia completa

- Jira: [COMLAB-11](https://g10-latam-equipo14.atlassian.net/browse/COMLAB-11)
- GitHub: [#64](https://github.com/No-Country-simulation/G10-ONE-equipo-14/issues/64)
- Issues existentes: [#36](https://github.com/No-Country-simulation/G10-ONE-equipo-14/issues/36), [#38](https://github.com/No-Country-simulation/G10-ONE-equipo-14/issues/38), [#39](https://github.com/No-Country-simulation/G10-ONE-equipo-14/issues/39)
- Propuesta de modelo: [data-model/CL-002_DATA_MODEL.md](data-model/CL-002_DATA_MODEL.md)

Objetivo: completar el modelo persistente antes de conectar IA y curaduría.

Entregables:

- Diseño de `analyses`, `opportunities`, `assets`, `asset_versions`, `approvals` y `manifests`.
- Relaciones, constraints e índices documentados.
- Migraciones Alembic con downgrade.
- Triggers únicamente cuando exista un requisito de integridad o auditoría aprobado.
- Consulta persistida de ejecuciones.
- Pruebas PostgreSQL.

### E3 — Pipeline de IA y decisión

- Jira: [COMLAB-12](https://g10-latam-equipo14.atlassian.net/browse/COMLAB-12)
- GitHub: [#65](https://github.com/No-Country-simulation/G10-ONE-equipo-14/issues/65)
- Issue existente: [#40](https://github.com/No-Country-simulation/G10-ONE-equipo-14/issues/40)

Objetivo: integrar el proveedor de análisis, decisiones, PII y quality gates con la API y PostgreSQL.

El repositorio ya contiene una implementación parcial de proveedor mock, análisis, detección de oportunidades y assets. La etapa debe verificarla, integrarla y persistir sus resultados; no se considera terminada por la sola existencia de clases aisladas.

### E4 — Generación de LinkedIn y FAQ

- Jira: [COMLAB-13](https://g10-latam-equipo14.atlassian.net/browse/COMLAB-13)
- GitHub: [#66](https://github.com/No-Country-simulation/G10-ONE-equipo-14/issues/66)

Objetivo: producir contenido trazable y validado mediante generadores independientes.

Entregables principales:

- Contrato `GeneratedAsset`.
- Generador de LinkedIn.
- Generador de FAQ.
- Prompts separados y versionados.
- Validaciones, persistencia de versiones y pruebas.

### E5 — Curaduría persistente en Streamlit

- Jira: [COMLAB-14](https://g10-latam-equipo14.atlassian.net/browse/COMLAB-14)
- GitHub: [#67](https://github.com/No-Country-simulation/G10-ONE-equipo-14/issues/67)
- Issue existente: [#41](https://github.com/No-Country-simulation/G10-ONE-equipo-14/issues/41)

Objetivo: revisar, editar, aprobar y rechazar activos con auditoría.

### E6 — OCI Object Storage y manifiestos

- Jira: [COMLAB-15](https://g10-latam-equipo14.atlassian.net/browse/COMLAB-15)
- GitHub: [#68](https://github.com/No-Country-simulation/G10-ONE-equipo-14/issues/68)
- Issue existente: [#42](https://github.com/No-Country-simulation/G10-ONE-equipo-14/issues/42)

Objetivo: publicar únicamente activos aprobados y generar manifiestos verificables con SHA-256, ETag y `schema_version`.

### E7 — Integración, pruebas y cierre del MVP

- Jira: [COMLAB-16](https://g10-latam-equipo14.atlassian.net/browse/COMLAB-16)
- GitHub: [#69](https://github.com/No-Country-simulation/G10-ONE-equipo-14/issues/69)
- Issue existente: [#43](https://github.com/No-Country-simulation/G10-ONE-equipo-14/issues/43)

Objetivo: validar los tres recorridos finales:

1. Logro de comunidad a borrador de LinkedIn aprobado.
2. Duda técnica a FAQ aprobada.
3. Contenido sensible detectado y bloqueado.

### E8 — Despliegue gratuito y operación

- Jira: [COMLAB-74](https://g10-latam-equipo14.atlassian.net/browse/COMLAB-74)
- GitHub: [#70](https://github.com/No-Country-simulation/G10-ONE-equipo-14/issues/70)
- Tickets Jira: COMLAB-75 a COMLAB-79

Objetivo: desplegar el MVP estable sin activar servicios pagos sin autorización explícita. La ruta OCI Free Tier quedó preparada, pero la demostración activa utiliza Render Free debido a la falta de capacidad de Compute en OCI.

## Próxima etapa

E2 a E5 ya no son trabajo futuro. El orden vigente, excluyendo temporalmente OCI, es:

1. **INV-021:** consolidar evidencias visuales E1-E6 y el recorrido final de curaduría/publicación local.
2. **INV-022:** documentar y, si aporta valor, implementar una entrada automática mínima.
3. **INV-023:** medir un lote de 500 interacciones y agregar una cola sólo si supera el objetivo de 30 segundos.
4. **INV-024:** ejecutar la evaluación de validez, grounding y precisión con una muestra revisable.
5. **INV-025 (completado):** decisión y criterios de canales posteriores al MVP documentados en `docs/CHANNEL_ROADMAP.md`; su implementación permanece fuera del MVP actual.
6. Ejecutar una auditoría final del inventario, issues, Jira y evidencias.
7. Recién entonces retomar **INV-002 a INV-005** para OCI Object Storage y el despliegue final.

Esta secuencia aplica la decisión del equipo: terminar primero la funcionalidad y dejar OCI para el cierre al 100%, sin eliminarlo del alcance obligatorio.

## Cierre de una épica

La épica se marca como finalizada solamente cuando:

- Todos los tickets obligatorios están cerrados.
- Los PR están integrados en `develop`.
- CI y pruebas locales están en verde.
- La documentación refleja el estado real.
- Las evidencias están disponibles.
- Jira y GitHub contienen enlaces recíprocos.
- La demostración de la etapa fue revisada.
