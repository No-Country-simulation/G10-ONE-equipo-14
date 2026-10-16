# Sets de prueba adicionales de CommunityLab

Esta carpeta contiene tres conjuntos independientes. Los archivos originales de `communitylab_ejemplos` no fueron modificados.

| Set | Tema | Registros | Análisis esperados | Oportunidades | Activos |
|---|---|---:|---:|---:|---:|
| 01 | Empleabilidad y formación tecnológica | 60 | 60 | 40 | 12 |
| 02 | Producto SaaS y comunidad de desarrolladores | 60 | 60 | 40 | 12 |
| 03 | Sostenibilidad e impacto social | 60 | 60 | 40 | 12 |

Cada set incluye `entrada_60.json`, `salida_esperada_60.json` y `manifest.json`.

## Compatibilidad del contrato de entrada

La API mantiene `author`, `channel`, `type` y `text` como nombres canónicos, y
acepta además los nombres presentes en estos sets (`author_alias` e
`interaction_type`) y en el documento original (`autor`, `canal`, `tipo` y
`texto`). Los tipos documentados en español se normalizan antes del análisis;
por ejemplo, `pregunta_tecnica` se procesa como `question` y `testimonio` como
`achievement`.

La carga CSV admite UTF-8 (recomendado) y Windows-1252 por compatibilidad con
archivos exportados por herramientas de escritorio.

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
