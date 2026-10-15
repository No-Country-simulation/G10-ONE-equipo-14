# INV-019 — Endurecimiento de CI

## Controles incorporados

- Ruff revisa lint y errores estáticos sobre API, dashboard y pruebas.
- El formateador de Ruff valida todos los archivos Python modificados por cada cambio, sin obligar a mezclar una reforma masiva del código histórico.
- `pip-audit` bloquea dependencias con vulnerabilidades conocidas; la auditoría detectó la versión anterior de pytest y se actualizó a una versión corregida.
- `py_compile` valida que los módulos Streamlit puedan compilarse y pytest cubre su cliente HTTP.
- La suite conserva migraciones Alembic, pruebas PostgreSQL y validación Terraform.
- Cada push a `main` verifica por HTTP el health público y que el dashboard de Render responda correctamente.

## Reproducción

Los comandos locales se documentan en el README y usan `requirements-dev.txt` para fijar las herramientas de calidad. La evidencia definitiva son los checks verdes de los PR de implementación y release.

Trazabilidad: GitHub #174 · Jira COMLAB-98.
