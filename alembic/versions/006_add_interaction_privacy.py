"""Add publication consent and opt-out to interactions.

Revision ID: 006_add_interaction_privacy
Revises: 005_unique_manifest_per_asset
"""

import sqlalchemy as sa
from alembic import op


revision = "006_add_interaction_privacy"
down_revision = "005_unique_manifest_per_asset"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("interactions", sa.Column("publication_consent", sa.Boolean(), server_default=sa.false(), nullable=False))
    op.add_column("interactions", sa.Column("opt_out", sa.Boolean(), server_default=sa.false(), nullable=False))
    op.add_column("interactions", sa.Column("pii_detected", sa.Boolean(), server_default=sa.false(), nullable=False))


def downgrade() -> None:
    op.drop_column("interactions", "pii_detected")
    op.drop_column("interactions", "opt_out")
    op.drop_column("interactions", "publication_consent")
