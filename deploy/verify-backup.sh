#!/bin/sh
set -eu

if [ "$#" -ne 1 ]; then
  echo "Usage: deploy/verify-backup.sh <backup.dump>" >&2
  exit 2
fi

backup_path="$1"
compose_file="${COMPOSE_FILE_PATH:-docker-compose.yml}"
postgres_user="${POSTGRES_USER:-communitylab}"
source_db="${POSTGRES_DB:-communitylab}"
verify_db="${VERIFY_DATABASE_NAME:-communitylab_restore_verify_$$}"

case "$verify_db" in
  *[!a-zA-Z0-9_]*)
    echo "VERIFY_DATABASE_NAME may contain only letters, numbers and underscores." >&2
    exit 2
    ;;
esac

test -s "$backup_path"

db_exec() {
  docker compose -f "$compose_file" exec -T db "$@"
}

cleanup() {
  db_exec psql -v ON_ERROR_STOP=1 -U "$postgres_user" -d postgres \
    -c "DROP DATABASE IF EXISTS \"$verify_db\" WITH (FORCE);" >/dev/null
}
trap cleanup EXIT INT TERM

cleanup
db_exec createdb -U "$postgres_user" "$verify_db"
db_exec pg_restore --exit-on-error --no-owner --no-privileges \
  -U "$postgres_user" -d "$verify_db" < "$backup_path"

required_tables="$(db_exec psql -At -v ON_ERROR_STOP=1 -U "$postgres_user" -d "$verify_db" -c \
  "SELECT count(*) FROM information_schema.tables WHERE table_schema='public' AND table_name IN ('alembic_version','runs','interactions','assets','manifests');")"
test "$required_tables" = "5"

restored_revision="$(db_exec psql -At -v ON_ERROR_STOP=1 -U "$postgres_user" -d "$verify_db" -c \
  'SELECT version_num FROM alembic_version;')"
test -n "$restored_revision"

count_query="SELECT 'assets=' || count(*) FROM assets UNION ALL SELECT 'interactions=' || count(*) FROM interactions UNION ALL SELECT 'runs=' || count(*) FROM runs ORDER BY 1;"
source_counts="$(db_exec psql -At -v ON_ERROR_STOP=1 -U "$postgres_user" -d "$source_db" -c "$count_query")"
restored_counts="$(db_exec psql -At -v ON_ERROR_STOP=1 -U "$postgres_user" -d "$verify_db" -c "$count_query")"
test "$source_counts" = "$restored_counts"

printf 'Restore verified: revision=%s; %s\n' "$restored_revision" "$(printf '%s' "$restored_counts" | tr '\n' ',')"
