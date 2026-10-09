# Ejemplos de entrada y salida de CommunityLab

## Contenido

- `entrada_interacciones_25.json`: lote con 25 interacciones sintéticas.
- `entrada_interacciones_25.csv`: el mismo lote en formato tabular para probar la carga CSV.
- `salida_procesada_ejemplo.json`: posible respuesta consolidada del aplicativo.
- `manifest_ejemplo.json`: ejemplo de trazabilidad y checksum para almacenamiento.

## Escenarios incluidos

El lote contiene testimonios, proyectos, preguntas técnicas, conversaciones neutras, problemas, feedback positivo, negativo y mixto, un caso de privacidad y un duplicado funcional. Todos los autores son alias sintéticos.

## Resultado esperado

El aplicativo debe validar el archivo, normalizar y deduplicar, analizar cada interacción, detectar oportunidades, generar borradores de LinkedIn y FAQ, exigir revisión humana y almacenar el paquete final en OCI Object Storage.

## Prueba sugerida

1. Enviar `entrada_interacciones_25.json` a `POST /api/v1/process` con una cabecera `Idempotency-Key`.
2. Verificar que se procesen 25 registros y que `INT-020` quede bloqueado por privacidad.
3. Comprobar que las conversaciones logísticas no generen contenido automáticamente.
4. Revisar que cada activo incluya `source_interaction_ids`.
5. Aprobar un activo, rechazar otro y validar el recibo de OCI.

La salida es ilustrativa. Los valores de relevancia, confianza, ETag y rutas deben ser generados por la implementación real.
