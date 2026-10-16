# Evidencia — cold start de Render

Fecha: 16 de octubre de 2026.

El dashboard público mostraba “API no disponible” porque su health check tenía
un timeout de 3 segundos. Una medición directa confirmó que la API de Render Free
tardó 33,75 segundos en despertar y luego respondió HTTP 200; las consultas
siguientes tardaron menos de un segundo.

## Corrección

- El health check se centralizó en `dashboard/api_client.py`.
- Su timeout pasó a 60 segundos para cubrir el arranque en frío gratuito.
- El mensaje visual explica que la API puede estar iniciando y solicita esperar y
  recargar, en lugar de afirmar inmediatamente que no está disponible.
- Una prueba comprueba endpoint y timeout para impedir la regresión.

## Verificación previa al release

| URL | Estado | Tiempo |
| --- | ---: | ---: |
| `https://communitylab-api.onrender.com/api/v1/health` | 200 | 33,75 s (cold start) |
| `https://communitylab-api.onrender.com/docs` | 200 | 0,33 s |
| `https://communitylab-dashboard.onrender.com/` | 200 | 0,31 s |

Después del release se repetirá el smoke público desde CI. La corrección no
modifica las mutaciones ni habilita escritura en la demo.
