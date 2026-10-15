# Evidencia INV-024 — métricas de evaluación

Fecha: 15 de octubre de 2026.

Se versionó una muestra humana de 20 interacciones con casos publicables,
irrelevantes, negativos y de privacidad. La guía describe la etiqueta, las
fórmulas y las limitaciones; el script reproduce la evaluación sin acceso a red.

## Resultado de línea base

| Métrica | Resultado | Umbral |
| --- | ---: | ---: |
| Validez contractual | 100% | 100% |
| Grounding exacto | 100% | 100% |
| Precisión de oportunidades públicas | 100% | ≥ 90% |
| Recall de oportunidades públicas | 90,91% | ≥ 90% |

Matriz de confusión: 10 verdaderos positivos, 9 verdaderos negativos, 0 falsos
positivos y 1 falso negativo. El caso `eval-008` muestra una brecha concreta: la
regla mock reconoce inteligencia artificial como tema, pero no alcanza el umbral
de relevancia cuando no detecta además una entidad. El resultado íntegro por
elemento queda en `result.json`.

## Alcance y limitaciones

- La muestra valida la lógica vigente con el proveedor mock reproducible.
- Es una muestra intencional de producto, no una muestra estadística aleatoria.
- Existe una sola etiqueta por caso; todavía no se mide acuerdo entre revisores.
- El falso negativo detectado debe usarse como línea base para mejorar recall sin
  degradar la precisión; no se cambió la etiqueta para embellecer el resultado.
- Una evaluación futura de Gemini debe añadirse como corrida separada porque sus
  resultados y costos pueden variar.

Archivos auditables:

- `data/evaluation/human_sample_v1.json` — muestra y razones humanas;
- `docs/EVALUATION_GUIDE.md` — definiciones y procedimiento;
- `scripts/evaluate_quality.py` — cálculo reproducible;
- `tests/test_quality_evaluation.py` — gates de regresión;
- `result.json` — salida completa de esta ejecución.
