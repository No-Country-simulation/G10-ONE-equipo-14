"""Create persistent internal alerts.

Revision ID: 007_create_alerts
Revises: 006_add_interaction_privacy
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "007_create_alerts"
down_revision = "006_add_interaction_privacy"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "alerts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("interaction_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("excerpt", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("severity IN ('MEDIUM', 'HIGH')", name="ck_alerts_severity"),
        sa.CheckConstraint("status IN ('OPEN', 'RESOLVED')", name="ck_alerts_status"),
        sa.CheckConstraint("length(btrim(message)) > 0", name="ck_alerts_message_nonempty"),
        sa.ForeignKeyConstraint(["interaction_id"], ["interactions.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["run_id"], ["runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_alerts_status_created", "alerts", ["status", "created_at"])
    op.create_index("ix_alerts_run", "alerts", ["run_id"])


def downgrade() -> None:
    op.drop_index("ix_alerts_run", table_name="alerts")
    op.drop_index("ix_alerts_status_created", table_name="alerts")
    op.drop_table("alerts")
