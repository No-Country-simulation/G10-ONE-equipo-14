# Interaction table — migration 001

The Pydantic contract `app/schemas/v1/interaction.py` validates HTTP input; the SQLAlchemy model `app/db/models/interaction.py` and Alembic migration enforce persistence constraints.

## Apply to local PostgreSQL

Start Docker Desktop, then from repository root:

```powershell
Copy-Item .env.example .env  # only if .env does not exist
 docker compose up -d --build
 docker compose exec api alembic upgrade head
 docker compose exec db psql -U communitylab -d communitylab -c "\d interactions"
```

`docker compose up` alone starts the database but does NOT apply the migration. Run `alembic upgrade head` once per new database/migration. Do not run `alembic downgrade` on databases containing data without a backup.

## Constraints

- UUID primary key (`id`); application supplies UUID when inserting.
- Non-null organization/community/author/channel/type/text/fingerprint.
- Nonempty (after trimming) organization/community/author/channel/type/text; optional external ID must be nonempty when present.
- `fingerprint` must contain exactly 64 lowercase hexadecimal characters.
- Unique `(organization_id, community_id, fingerprint)` and `(organization_id, community_id, external_id)`; PostgreSQL permits multiple NULL external IDs.
- `created_at` defaults to database server time; `occurred_at` is optional timezone-aware timestamp.
- Index on organization/community/created_at for scoped retrieval.

The existing `/process` endpoint remains a mock and does NOT persist interactions yet. A subsequent ingestion PR must calculate fingerprints, insert rows, handle uniqueness violations and implement persisted idempotency.

## Validation

`pytest -q` checks model metadata. Optional PostgreSQL integration test requires `TEST_DATABASE_URL` pointing to an isolated test database. The database must be running to execute migrations.
