"""Create runs table for request idempotency.

Revision ID: 002_create_runs
Revises: 001_create_interactions
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "002_create_runs"
down_revision = "001_create_interactions"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "runs",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column("organization_id", sa.String(100), nullable=False),
        sa.Column("community_id", sa.String(100), nullable=False),
        sa.Column("idempotency_key", sa.String(255), nullable=False),
        sa.Column("request_hash", sa.String(64), nullable=False),
        sa.Column(
            "status",
            sa.String(40),
            nullable=False,
            server_default="PROCESSING",
        ),
        sa.Column("response_json", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "organization_id",
            "community_id",
            "idempotency_key",
            name="uq_runs_idempotency_per_community",
        ),
        sa.CheckConstraint(
            "length(btrim(organization_id)) > 0",
            name="ck_runs_organization_nonempty",
        ),
        sa.CheckConstraint(
            "length(btrim(community_id)) > 0",
            name="ck_runs_community_nonempty",
        ),
        sa.CheckConstraint(
            "length(btrim(idempotency_key)) > 0",
            name="ck_runs_idempotency_key_nonempty",
        ),
        sa.CheckConstraint(
            "request_hash ~ '^[0-9a-f]{64}$'",
            name="ck_runs_request_hash_sha256",
        ),
    )

    op.create_index(
        "ix_runs_community_created",
        "runs",
        ["organization_id", "community_id", "created_at"],
    )


def downgrade():
    op.drop_index("ix_runs_community_created", table_name="runs")
    op.drop_table("runs")
