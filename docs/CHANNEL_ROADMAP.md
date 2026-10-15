# Roadmap de canales adicionales

Estado de decisión: aprobado para planificación posterior al MVP.

CommunityLab mantiene LinkedIn y FAQ como salidas del MVP. Los canales de este
documento no se implementan todavía: incorporarlos antes de cerrar el despliegue
final aumentaría el riesgo sin resolver una brecha obligatoria. La decisión de
INV-025 define orden, límites y criterios para que el trabajo futuro no quede
ambiguo.

## Prioridad acordada

| Orden | Capacidad | Decisión | Motivo |
| ---: | --- | --- | --- |
| 1 | Highlights semanales | Siguiente incremento recomendado | Reutiliza activos y fuentes existentes, no exige proveedor externo y ofrece valor visible inmediato. |
| 2 | Informe de sentimiento | Incremento interno | Aprovecha análisis persistidos; debe mostrar agregados y no exponer textos o identidades. |
| 3 | Newsletter | Posterior | Requiere composición de varios activos, preferencias de suscripción, preview y proveedor de envío. |
| 4 | X/Twitter | Diferido | Depende de API, OAuth, límites/costos cambiantes y políticas de la plataforma; no es requisito del MVP. |

OCI no es una dependencia para diseñar o generar estas salidas, pero sí forma
parte del cierre de publicación persistente del proyecto y se abordará en su fase
separada INV-002 a INV-005.

## Contrato común futuro

Cada generador debe recibir una oportunidad aprobable y producir un activo
versionado con:

- `channel`, título opcional, cuerpo y versión;
- `source_interaction_ids` y excerpts exactos;
- modelo y versión de prompt;
- estado inicial `PENDING_REVIEW`;
- reglas de longitud y contenido específicas del canal.

Ningún adaptador puede publicar al generarse el activo. Edición, aprobación y
publicación siguen siendo pasos separados, auditables e idempotentes. Opt-out,
consentimiento, anonimización, PII y alertas internas se aplican antes de todos
los canales.

## Criterios por incremento

### Highlights semanales

- agrupar por comunidad y periodo de referencia;
- seleccionar únicamente oportunidades públicas no bloqueadas;
- evitar duplicar una fuente dentro del mismo resumen;
- conservar fuentes por cada highlight;
- generar preview, editar y aprobar desde la cola actual;
- pruebas de periodo vacío, deduplicación, consentimiento y trazabilidad.

### Informe de sentimiento

- presentar conteos y porcentajes agregados por periodo;
- separar alertas internas de contenido publicable;
- aplicar un mínimo de muestra antes de mostrar segmentos para evitar
  reidentificación;
- no incluir autores ni excerpts en la vista agregada;
- documentar que describe la muestra observada y no a toda la comunidad.

### Newsletter

- componer secciones desde activos previamente aprobados;
- exigir preview y aprobación final del envío completo;
- conservar versión del contenido y fuentes de cada sección;
- integrar proveedor mediante adaptador, sin tokens en base ni repositorio;
- manejar bajas, consentimiento de destinatarios, reintentos e idempotencia;
- modo sandbox obligatorio antes de habilitar envíos reales.

### X/Twitter

- confirmar primero disponibilidad, costo y términos vigentes de la API;
- usar OAuth con secretos externos al repositorio;
- validar longitud y dividir hilos de forma determinística;
- no publicar nombres, citas ni multimedia sin consentimiento explícito;
- exigir aprobación humana y almacenar el identificador/URL de publicación;
- manejar límites, reintentos y duplicados sin repetir publicaciones.

## Gate para iniciar cada canal

Un incremento sólo pasa a desarrollo cuando tenga responsable, issue GitHub y
ticket Jira enlazados, criterio de éxito medible, diseño aprobado, proveedor y
costos confirmados cuando corresponda, y un plan de prueba que incluya privacidad
y fallos. La entrega sigue el mismo flujo: rama, PR a `develop`, CI, release a
`main`, evidencia y cierre recíproco de tickets.

## Fuera de alcance de esta decisión

- implementar o contratar proveedores externos;
- crear cuentas, credenciales o campañas reales;
- publicar automáticamente sin curaduría;
- sustituir las tareas OCI pendientes;
- prometer fechas o costos sin validar las condiciones del proveedor.
