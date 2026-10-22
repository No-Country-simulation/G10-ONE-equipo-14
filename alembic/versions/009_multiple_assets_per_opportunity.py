"""Allow multiple distinct assets per content opportunity.

Revision ID: 009_multi_assets_per_opp
Revises: 008_create_processing_jobs
"""

from alembic import op

revision = "009_multi_assets_per_opp"
down_revision = "008_create_processing_jobs"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("uq_assets_opportunity_type", "assets", type_="unique")


def downgrade() -> None:
    op.create_unique_constraint(
        "uq_assets_opportunity_type", "assets", ["opportunity_id", "asset_type"]
    )
