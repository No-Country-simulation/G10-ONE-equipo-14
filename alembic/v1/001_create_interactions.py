"""Create interactions table and integrity constraints.

Revision ID: 001_create_interactions
Revises:
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001_create_interactions"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "interactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("organization_id", sa.String(100), nullable=False),
        sa.Column("community_id", sa.String(100), nullable=False),
        sa.Column("external_id", sa.String(255), nullable=True),
        sa.Column("author", sa.String(200), nullable=False),
        sa.Column("channel", sa.String(200), nullable=False),
        sa.Column("type", sa.String(100), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("fingerprint", sa.String(64), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("organization_id", "community_id", "external_id", name="uq_interactions_external_per_community"),
        sa.UniqueConstraint("organization_id", "community_id", "fingerprint", name="uq_interactions_fingerprint_per_community"),
        sa.CheckConstraint("length(btrim(organization_id)) > 0", name="ck_interactions_organization_nonempty"),
        sa.CheckConstraint("length(btrim(community_id)) > 0", name="ck_interactions_community_nonempty"),
        sa.CheckConstraint("length(btrim(author)) > 0", name="ck_interactions_author_nonempty"),
        sa.CheckConstraint("length(btrim(channel)) > 0", name="ck_interactions_channel_nonempty"),
        sa.CheckConstraint("length(btrim(type)) > 0", name="ck_interactions_type_nonempty"),
        sa.CheckConstraint("length(btrim(text)) > 0", name="ck_interactions_text_nonempty"),
        sa.CheckConstraint("external_id IS NULL OR length(btrim(external_id)) > 0", name="ck_interactions_external_nonempty"),
        sa.CheckConstraint("fingerprint ~ '^[0-9a-f]{64}$'", name="ck_interactions_fingerprint_sha256"),
    )
    op.create_index("ix_interactions_community_created", "interactions", ["organization_id", "community_id", "created_at"])

def downgrade():
    op.drop_index("ix_interactions_community_created", table_name="interactions")
    op.drop_table("interactions")
