# Guía de evaluación humana

Esta guía define la muestra y las métricas de calidad de CommunityLab. Su objetivo
es permitir comparar cambios de reglas, prompts o modelos con el mismo criterio.

## Unidad y etiquetado

Cada fila representa una interacción. Una persona revisora registra:

- `expected_public_opportunity`: `true` si el texto justifica crear un borrador
  público; `false` para coordinación cotidiana, contenido irrelevante, opt-out o
  casos negativos que deban dirigirse a una alerta interna;
- `rationale`: motivo breve y verificable de la etiqueta;
- consentimiento y opt-out, que prevalecen sobre el interés editorial.

La muestra `data/evaluation/human_sample_v1.json` contiene casos positivos,
negativos, irrelevantes y de privacidad. Es una línea base de producto anotada
por el rol de product owner; no pretende medir acuerdo entre múltiples personas.

## Métricas

1. **Validez de salida:** proporción de análisis que vuelven a validar contra el
   contrato Pydantic `Analysis`.
2. **Grounding:** proporción con al menos una evidencia cuyo identificador apunta
   a la interacción evaluada y cuyo excerpt existe literalmente en el texto.
3. **Precisión de oportunidades:** `TP / (TP + FP)` para oportunidades públicas
   con estado `PENDING`, frente a la etiqueta humana.
4. **Recall auxiliar:** `TP / (TP + FN)`, publicado para impedir que una precisión
   alta oculte un sistema que no propone oportunidades.

La línea base automatizada exige 100% de validez, 100% de grounding y al menos
90% de precisión y recall. Estos umbrales son gates de regresión, no una garantía
estadística de calidad general.

## Ejecución

```powershell
docker compose run --rm -T api python -m scripts.evaluate_quality
```

Para guardar un reporte:

```powershell
docker compose run --rm -T api python -m scripts.evaluate_quality --output docs/evidence/INV-024-quality-evaluation/result.json
```

Al evaluar Gemini, se debe conservar la muestra, registrar modelo y versión de
prompt, y agregar una corrida separada; nunca reemplazar silenciosamente la línea
base determinística.
