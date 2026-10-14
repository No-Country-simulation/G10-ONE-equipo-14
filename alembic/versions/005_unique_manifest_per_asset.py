"""Ensure that each asset has at most one publication manifest.

Revision ID: 005_unique_manifest_per_asset
Revises: 004_add_updated_at_triggers
"""

from alembic import op


revision = "005_unique_manifest_per_asset"
down_revision = "004_add_updated_at_triggers"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint("uq_manifests_asset_id", "manifests", ["asset_id"])


def downgrade() -> None:
    op.drop_constraint("uq_manifests_asset_id", "manifests", type_="unique")
