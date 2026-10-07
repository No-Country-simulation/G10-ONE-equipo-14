# Guion de demostración y cierre del MVP

## Preparación

1. Copiar `.env.example` a `.env`.
2. Ejecutar `docker compose up -d --build`.
3. Abrir `http://localhost:8501` y confirmar API y PostgreSQL.
4. Usar `data/sample_interactions.json` o `data/sample_interactions.csv`.

## Recorridos obligatorios

1. **Logro → LinkedIn**: procesar, revisar, editar, aprobar y publicar.
2. **Duda → FAQ**: procesar una duda técnica y aprobar la FAQ trazable.
3. **PII bloqueada**: procesar texto con correo o teléfono y comprobar que no genera assets.

## Definition of Done

- Migraciones upgrade/downgrade verificadas.
- Suite local y CI en verde.
- Ningún secreto versionado.
- GitHub y Jira enlazados y finalizados.
- Docker Compose reproducible.
- Tres recorridos demostrables.
- Producción documenta HTTPS, secretos, backup y smoke tests.
