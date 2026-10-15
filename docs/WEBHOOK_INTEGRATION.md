# Entrada automática por webhook

CommunityLab ofrece un adaptador neutral en `POST /api/v1/webhooks/interactions`. Recibe una interacción por evento y la transforma en el mismo `ProcessRequest` usado por JSON/CSV; no existe un pipeline paralelo.

## Contrato

```json
{
  "schema_version": "v1",
  "source": "discord",
  "event_id": "1234567890",
  "organization_id": "one",
  "community_id": "g10-equipo-14",
  "reference_period": "2026-W42",
  "requested_assets": ["LINKEDIN", "FAQ"],
  "interaction": {
    "author": "usuario-anonimo",
    "channel": "logros",
    "type": "message",
    "text": "Terminé mi proyecto de automatización.",
    "occurred_at": "2026-10-15T12:00:00Z",
    "publication_consent": true,
    "opt_out": false
  }
}
```

Si `interaction.external_id` no viene informado, CommunityLab usa `<source>:<event_id>`. La idempotencia de la ejecución usa `webhook:<source>:<event_id>`.

## Prueba local

```bash
curl --request POST http://localhost:8000/api/v1/webhooks/interactions \
  --header 'Content-Type: application/json' \
  --header 'X-API-Key: <clave-sólo-si-está-configurada>' \
  --data @webhook-event.json
```

La respuesta HTTP 202 es el `ProcessResponse` habitual, incluido `run_id`, resumen, análisis, oportunidades, activos y alertas.

## Mapeos

### n8n

Usar un nodo Webhook o el trigger del proveedor y un nodo HTTP Request:

- Method: `POST`.
- URL: `<API_URL>/api/v1/webhooks/interactions`.
- Header `X-API-Key`: credencial de n8n, nunca texto fijo exportado al workflow.
- `source`: nombre estable del conector.
- `event_id`: identificador original e inmutable del evento.
- Body: JSON del contrato anterior.

### Discord

Un bot o workflow debe mapear `message.id` a `event_id`, `channel_id/name` a `interaction.channel`, `author.id` a un identificador seudónimo y `content` a `text`. No enviar nombre, correo ni token del bot. `publication_consent` debe provenir de una regla explícita del servidor; su ausencia equivale a `false`.

### Slack

Mapear `event_id` (o `event_ts` estable) a `event_id`, `channel` a `interaction.channel`, un identificador seudónimo a `author` y `text` al cuerpo. Verificar la firma de Slack en el componente que recibe el evento antes de llamar a CommunityLab; este endpoint autentica al conector con la clave de escritura, no reemplaza la validación propia del proveedor.

## Reintentos y errores

- Mismo evento y mismo contenido: HTTP 202 con el mismo `run_id`.
- Mismo evento y contenido diferente: HTTP 409.
- Mutaciones deshabilitadas: HTTP 403.
- Clave ausente/incorrecta cuando está configurada: HTTP 401.
- Límite excedido: HTTP 429.
- Contrato inválido: HTTP 422.

El despliegue público de Render permanece en modo sólo lectura. Para activar el webhook en un entorno compartido, deben configurarse `MUTATIONS_ENABLED=true` y el mismo `API_WRITE_KEY` secreto en el emisor y la API.
