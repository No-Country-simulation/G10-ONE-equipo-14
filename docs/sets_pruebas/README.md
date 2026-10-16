# Sets de prueba adicionales de CommunityLab

Esta carpeta contiene tres conjuntos independientes. Los archivos originales de `communitylab_ejemplos` no fueron modificados.

| Set | Tema | Registros | Análisis esperados | Oportunidades | Activos |
|---|---|---:|---:|---:|---:|
| 01 | Empleabilidad y formación tecnológica | 60 | 60 | 40 | 12 |
| 02 | Producto SaaS y comunidad de desarrolladores | 60 | 60 | 40 | 12 |
| 03 | Sostenibilidad e impacto social | 60 | 60 | 40 | 12 |

Cada set incluye `entrada_60.json`, `salida_esperada_60.json` y `manifest.json`.

## Distribución de casos por set

- 10 logros o testimonios.
- 10 preguntas técnicas.
- 10 comentarios positivos.
- 10 problemas o feedback negativo.
- 10 mensajes neutros que no deben generar contenido.
- 10 mensajes sensibles que deben bloquearse por privacidad.

## Criterios esperados

- Los 60 registros producen un análisis.
- Los mensajes neutros no crean oportunidades.
- Los casos sensibles quedan bloqueados.
- Todos los activos contienen `source_interaction_ids`.
- Las salidas incluyen resumen, oportunidades, activos y rutas esperadas de OCI.

## Mejora implementada: compatibilidad del contrato de entrada

La API mantiene los siguientes nombres como contrato canónico:

| Dato | Nombre canónico | Alternativas admitidas |
|---|---|---|
| Autor | `author` | `author_alias`, `autor` |
| Canal | `channel` | `canal` |
| Tipo de interacción | `type` | `interaction_type`, `tipo` |
| Contenido | `text` | `texto` |

Los tipos documentados en español se normalizan antes del análisis. Algunos
ejemplos son:

| Valor recibido | Valor normalizado |
|---|---|
| `pregunta_tecnica` | `question` |
| `testimonio` | `achievement` |
| `proyecto_destacado` | `achievement` |
| `conversacion` | `message` |
| `problema` o `feedback_negativo` | `problem` |
| `alerta_privacidad` | `privacy_alert` |

La carga CSV admite UTF-8, que continúa siendo la codificación recomendada, y
Windows-1252 para archivos exportados por herramientas de escritorio. También
acepta fechas con formato ISO 8601 o `DD/MM/YYYY HH:MM`.

Esta compatibilidad está cubierta por pruebas automáticas que validan los cuatro
archivos JSON de entrada y las 25 filas del CSV del set 04. Las salidas esperadas
son referencias funcionales: los valores de relevancia, confianza y cantidades
de oportunidades o activos pueden variar cuando se utiliza un modelo LLM real.
