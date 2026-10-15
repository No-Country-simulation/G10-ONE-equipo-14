"""Create durable asynchronous processing jobs.

Revision ID: 008_create_processing_jobs
Revises: 007_create_alerts
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "008_create_processing_jobs"
down_revision = "007_create_alerts"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "processing_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", sa.String(100), nullable=False),
        sa.Column("community_id", sa.String(100), nullable=False),
        sa.Column("idempotency_key", sa.String(255), nullable=False),
        sa.Column("request_hash", sa.String(64), nullable=False),
        sa.Column("request_json", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(20), server_default="QUEUED", nullable=False),
        sa.Column("run_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("attempts", sa.Integer(), server_default="0", nullable=False),
        sa.Column("error_type", sa.String(100), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('QUEUED', 'RUNNING', 'SUCCEEDED', 'FAILED')",
            name="ck_processing_jobs_status",
        ),
        sa.CheckConstraint("attempts >= 0", name="ck_processing_jobs_attempts"),
        sa.ForeignKeyConstraint(["run_id"], ["runs.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "organization_id",
            "community_id",
            "idempotency_key",
            name="uq_processing_jobs_idempotency_per_community",
        ),
    )
    op.create_index(
        "ix_processing_jobs_status_created", "processing_jobs", ["status", "created_at"]
    )
    op.execute(
        """
        CREATE TRIGGER trg_processing_jobs_set_updated_at
        BEFORE UPDATE ON processing_jobs
        FOR EACH ROW EXECUTE FUNCTION set_updated_at()
        """
    )


def downgrade() -> None:
    op.execute(
        "DROP TRIGGER IF EXISTS trg_processing_jobs_set_updated_at ON processing_jobs"
    )
    op.drop_index("ix_processing_jobs_status_created", table_name="processing_jobs")
    op.drop_table("processing_jobs")
