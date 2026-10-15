# Evidencia INV-012

Fecha: 14 de octubre de 2026.

## Comportamiento verificado

- Una pregunta aislada no genera FAQ.
- Dos o más preguntas del mismo tema alcanzan el umbral predeterminado.
- La recurrencia produce una sola FAQ, no una por interacción.
- El activo conserva los identificadores y extractos de todas las preguntas agrupadas.
- Interacciones que no son de tipo `question` no cuentan para la recurrencia.
- La generación de LinkedIn continúa siendo independiente.

## Validación

```text
120 passed, 1 warning in 19.29s
```

Trazabilidad: GitHub #153 / Jira COMLAB-91.
