# INV-018 — Respaldo y restauración verificados

## Procedimiento

1. `deploy/backup.sh` ejecuta `pg_dump --format=custom`, comprueba que el archivo no esté vacío y valida su catálogo con `pg_restore --list`.
2. `deploy/verify-backup.sh` crea una base temporal con nombre único.
3. El dump se restaura usando `pg_restore --exit-on-error`.
4. Se comprueban la revisión Alembic, las tablas críticas y los conteos de `runs`, `interactions` y `assets` contra la base origen.
5. Un `trap` elimina siempre la base temporal; la base de la aplicación nunca es destino de restauración.

## Ejecución local

La prueba se ejecutó contra PostgreSQL 16 del entorno Docker Compose. El dump se generó correctamente, se restauró en una base aislada, las verificaciones coincidieron y la base temporal se eliminó al finalizar.

Resultado observado el 15 de octubre de 2026:

```text
Restore verified: revision=007_create_alerts; assets=80,interactions=80,runs=5
```

Los archivos de backup no se versionan: contienen datos de operación y deben almacenarse cifrados en un medio persistente. Render Free no se considera respaldo.

Trazabilidad: GitHub #171 · Jira COMLAB-97.
