#!/bin/sh
set -eu

backup_dir="${BACKUP_DIR:-./backups}"
compose_file="${COMPOSE_FILE_PATH:-docker-compose.yml}"
postgres_user="${POSTGRES_USER:-communitylab}"
postgres_db="${POSTGRES_DB:-communitylab}"
retention_days="${BACKUP_RETENTION_DAYS:-7}"

mkdir -p "$backup_dir"
timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
backup_path="$backup_dir/communitylab-$timestamp.dump"

# The custom format includes schema and data, is compressed by pg_dump, and can
# be validated by pg_restore without modifying the source database.
docker compose -f "$compose_file" exec -T db \
  pg_dump --format=custom --no-owner --no-privileges \
  -U "$postgres_user" -d "$postgres_db" > "$backup_path"

test -s "$backup_path"
docker compose -f "$compose_file" exec -T db pg_restore --list < "$backup_path" >/dev/null
find "$backup_dir" -type f -name 'communitylab-*.dump' -mtime "+$retention_days" -delete

printf '%s\n' "$backup_path"
