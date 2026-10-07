"""Create persistent content, curation and manifest entities.

Revision ID: 003_create_content_entities
Revises: 002_create_runs
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "003_create_content_entities"
down_revision = "002_create_runs"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "analyses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("run_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("interaction_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("interactions.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("schema_version", sa.String(20), nullable=False),
        sa.Column("sentiment", sa.String(40), nullable=False),
        sa.Column("topics", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("entities", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("relevance", sa.Numeric(5, 4), nullable=False),
        sa.Column("confidence", sa.Numeric(5, 4), nullable=False),
        sa.Column("model", sa.String(120), nullable=False),
        sa.Column("prompt_version", sa.String(80), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("run_id", "interaction_id", name="uq_analyses_run_interaction"),
        sa.CheckConstraint("length(btrim(schema_version)) > 0", name="ck_analyses_schema_version_nonempty"),
        sa.CheckConstraint("length(btrim(sentiment)) > 0", name="ck_analyses_sentiment_nonempty"),
        sa.CheckConstraint("relevance >= 0 AND relevance <= 1", name="ck_analyses_relevance_range"),
        sa.CheckConstraint("confidence >= 0 AND confidence <= 1", name="ck_analyses_confidence_range"),
        sa.CheckConstraint("length(btrim(model)) > 0", name="ck_analyses_model_nonempty"),
        sa.CheckConstraint("length(btrim(prompt_version)) > 0", name="ck_analyses_prompt_version_nonempty"),
    )
    op.create_index("ix_analyses_run_created", "analyses", ["run_id", "created_at"])
    op.create_index("ix_analyses_interaction", "analyses", ["interaction_id"])

    op.create_table(
        "analysis_evidence",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("analysis_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("interaction_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("interactions.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("excerpt", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("analysis_id", "interaction_id", "excerpt", name="uq_analysis_evidence_source_excerpt"),
        sa.CheckConstraint("length(btrim(excerpt)) > 0", name="ck_analysis_evidence_excerpt_nonempty"),
    )

    op.create_table(
        "opportunities",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("run_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("analysis_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("schema_version", sa.String(20), nullable=False),
        sa.Column("kind", sa.String(60), nullable=False),
        sa.Column("priority", sa.Numeric(5, 4), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("length(btrim(schema_version)) > 0", name="ck_opportunities_schema_version_nonempty"),
        sa.CheckConstraint("length(btrim(kind)) > 0", name="ck_opportunities_kind_nonempty"),
        sa.CheckConstraint("priority >= 0 AND priority <= 1", name="ck_opportunities_priority_range"),
        sa.CheckConstraint("length(btrim(reason)) > 0", name="ck_opportunities_reason_nonempty"),
        sa.CheckConstraint("status IN ('PENDING', 'REVIEW_REQUIRED', 'BLOCKED')", name="ck_opportunities_status"),
    )
    op.create_index("ix_opportunities_run_status_created", "opportunities", ["run_id", "status", "created_at"])
    op.create_index("ix_opportunities_analysis", "opportunities", ["analysis_id"])

    op.create_table(
        "opportunity_sources",
        sa.Column("opportunity_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("opportunities.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("interaction_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("interactions.id", ondelete="RESTRICT"), primary_key=True),
    )

    op.create_table(
        "assets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("run_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("opportunity_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("opportunities.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("schema_version", sa.String(20), nullable=False),
        sa.Column("asset_type", sa.String(40), nullable=False),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("current_version_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("opportunity_id", "asset_type", name="uq_assets_opportunity_type"),
        sa.CheckConstraint("length(btrim(schema_version)) > 0", name="ck_assets_schema_version_nonempty"),
        sa.CheckConstraint("asset_type IN ('LINKEDIN', 'FAQ')", name="ck_assets_type"),
        sa.CheckConstraint("status IN ('PENDING_REVIEW', 'APPROVED', 'REJECTED')", name="ck_assets_status"),
    )
    op.create_index("ix_assets_status_created", "assets", ["status", "created_at"])

    op.create_table(
        "asset_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("assets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("content", postgresql.JSONB(), nullable=False),
        sa.Column("model", sa.String(120), nullable=True),
        sa.Column("prompt_version", sa.String(80), nullable=True),
        sa.Column("created_by", sa.String(200), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("asset_id", "version_number", name="uq_asset_versions_number"),
        sa.CheckConstraint("version_number > 0", name="ck_asset_versions_number_positive"),
        sa.CheckConstraint("length(btrim(title)) > 0", name="ck_asset_versions_title_nonempty"),
        sa.CheckConstraint("length(btrim(created_by)) > 0", name="ck_asset_versions_created_by_nonempty"),
    )
    op.create_foreign_key(
        "fk_assets_current_version",
        "assets",
        "asset_versions",
        ["current_version_id"],
        ["id"],
        ondelete="RESTRICT",
    )

    op.create_table(
        "asset_version_sources",
        sa.Column("asset_version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("asset_versions.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("interaction_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("interactions.id", ondelete="RESTRICT"), primary_key=True),
        sa.Column("excerpt", sa.Text(), primary_key=True),
        sa.CheckConstraint("length(btrim(excerpt)) > 0", name="ck_asset_version_sources_excerpt_nonempty"),
    )

    op.create_table(
        "approvals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("assets.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("asset_version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("asset_versions.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("reviewer", sa.String(200), nullable=False),
        sa.Column("decision", sa.String(20), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("length(btrim(reviewer)) > 0", name="ck_approvals_reviewer_nonempty"),
        sa.CheckConstraint("decision IN ('APPROVED', 'REJECTED')", name="ck_approvals_decision"),
    )
    op.create_index("ix_approvals_asset_created", "approvals", ["asset_id", "created_at"])

    op.create_table(
        "manifests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("run_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("runs.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("assets.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("schema_version", sa.String(20), nullable=False),
        sa.Column("bucket", sa.String(255), nullable=False),
        sa.Column("object_key", sa.Text(), nullable=False),
        sa.Column("content_type", sa.String(150), nullable=False),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column("etag", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("bucket", "object_key", name="uq_manifests_bucket_object_key"),
        sa.CheckConstraint("length(btrim(schema_version)) > 0", name="ck_manifests_schema_version_nonempty"),
        sa.CheckConstraint("length(btrim(bucket)) > 0", name="ck_manifests_bucket_nonempty"),
        sa.CheckConstraint("length(btrim(object_key)) > 0", name="ck_manifests_object_key_nonempty"),
        sa.CheckConstraint("length(btrim(content_type)) > 0", name="ck_manifests_content_type_nonempty"),
        sa.CheckConstraint("sha256 ~ '^[0-9a-f]{64}$'", name="ck_manifests_sha256"),
    )
    op.create_index("ix_manifests_run", "manifests", ["run_id"])


def downgrade():
    op.drop_index("ix_manifests_run", table_name="manifests")
    op.drop_table("manifests")
    op.drop_index("ix_approvals_asset_created", table_name="approvals")
    op.drop_table("approvals")
    op.drop_table("asset_version_sources")
    op.drop_constraint("fk_assets_current_version", "assets", type_="foreignkey")
    op.drop_table("asset_versions")
    op.drop_index("ix_assets_status_created", table_name="assets")
    op.drop_table("assets")
    op.drop_table("opportunity_sources")
    op.drop_index("ix_opportunities_analysis", table_name="opportunities")
    op.drop_index("ix_opportunities_run_status_created", table_name="opportunities")
    op.drop_table("opportunities")
    op.drop_table("analysis_evidence")
    op.drop_index("ix_analyses_interaction", table_name="analyses")
    op.drop_index("ix_analyses_run_created", table_name="analyses")
    op.drop_table("analyses")
