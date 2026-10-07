#!/bin/sh
set -eu
backup_dir="${BACKUP_DIR:-/opt/communitylab/backups}"
mkdir -p "$backup_dir"
timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
docker compose -f /opt/communitylab/deploy/compose.prod.yml exec -T db \
  pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" | gzip > "$backup_dir/communitylab-$timestamp.sql.gz"
find "$backup_dir" -type f -name 'communitylab-*.sql.gz' -mtime +7 -delete
