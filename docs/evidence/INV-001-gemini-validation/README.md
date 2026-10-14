# Evidencia INV-001 - proveedor Gemini real

Fecha: 14 de octubre de 2026.

## Configuración validada

- Proveedor: `gemini`
- Modelo: `gemini-3.1-flash-lite`
- Fallback explícito: `mock`
- Credencial: variable local `GEMINI_API_KEY`, excluida de Git
- Entrada: `data/sample_interactions.json`

## Recorrido real

- Run ID: `bdc11ba4-0b40-4a15-b909-16f2e8fae50a`
- Interacciones recibidas: 20
- Interacciones aceptadas: 20
- Errores: 0
- Análisis estructurados: 20
- Análisis con evidencia textual: 20
- Análisis producidos por `gemini-3.1-flash-lite`: 20
- Oportunidades: 20
- Activos generados: 40

## Fallback comprobado

Antes del recorrido definitivo, Google respondió `503 UNAVAILABLE` para un
modelo con demanda alta. El pipeline agotó sus intentos y procesó las 20
interacciones con `mock-analysis-v1`, sin interrumpir la ejecución. Luego se
seleccionó el modelo estable disponible y se repitió el lote íntegramente con
Gemini real.

La clave no aparece en este documento, en los logs versionados ni en el
repositorio.
