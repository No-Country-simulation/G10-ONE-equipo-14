# Interaction table — migration 001

The Pydantic contract `app/schemas/v1/interaction.py` validates HTTP input; the SQLAlchemy model `app/db/models/interaction.py` and Alembic migration enforce persistence constraints.

## Apply to local PostgreSQL

Start Docker Desktop, then from repository root:

```powershell
Copy-Item .env.example .env  # only if .env does not exist
docker compose up -d --build
docker compose exec db psql -U communitylab -d communitylab -c "\d interactions"
```

The API service runs `python -m alembic upgrade head` before starting Uvicorn. If a migration fails, the API does not report healthy and the dashboard waits instead of connecting to an incomplete database.

Do not run `alembic downgrade` on databases containing data without a backup. CI verifies upgrade and downgrade only against its isolated `communitylab_test` database.

## Constraints

- UUID primary key (`id`); application supplies UUID when inserting.
- Non-null organization/community/author/channel/type/text/fingerprint.
- Nonempty (after trimming) organization/community/author/channel/type/text; optional external ID must be nonempty when present.
- `fingerprint` must contain exactly 64 lowercase hexadecimal characters.
- Unique `(organization_id, community_id, fingerprint)` and `(organization_id, community_id, external_id)`; PostgreSQL permits multiple NULL external IDs.
- `created_at` defaults to database server time; `occurred_at` is optional timezone-aware timestamp.
- Index on organization/community/created_at for scoped retrieval.

`POST /api/v1/process` and `POST /api/v1/process/csv` persist normalized interactions and calculate fingerprints. A repeated interaction reuses its stored interaction row but is analyzed again in each new run; repeated copies within one upload are analyzed once. A repeated `Idempotency-Key` still replays its original run response. `GET /api/v1/runs/{run_id}` retrieves that response: it returns HTTP 404 for an unknown UUID and HTTP 409 only while an existing run has no completed response. The dashboard exposes this lookup through its **Run ID** field.

## Validation

`python -m pytest -q tests` checks model metadata and the complete application flow. PostgreSQL tests require `TEST_DATABASE_URL` pointing to an isolated database; Docker and CI create/use `communitylab_test` for that purpose. CI also exercises every Alembic upgrade and downgrade against the isolated database.
