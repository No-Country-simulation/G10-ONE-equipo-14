import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AssetRecord(Base):
    __tablename__ = "assets"
    __table_args__ = (
        UniqueConstraint("opportunity_id", "asset_type", name="uq_assets_opportunity_type"),
        CheckConstraint("length(btrim(schema_version)) > 0", name="ck_assets_schema_version_nonempty"),
        CheckConstraint("asset_type IN ('LINKEDIN', 'FAQ')", name="ck_assets_type"),
        CheckConstraint("status IN ('PENDING_REVIEW', 'APPROVED', 'REJECTED')", name="ck_assets_status"),
        Index("ix_assets_status_created", "status", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("runs.id", ondelete="CASCADE"), nullable=False)
    opportunity_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("opportunities.id", ondelete="RESTRICT"), nullable=False)
    schema_version: Mapped[str] = mapped_column(String(20), nullable=False, default="v1")
    asset_type: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="PENDING_REVIEW")
    current_version_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("asset_versions.id", name="fk_assets_current_version", use_alter=True, ondelete="RESTRICT"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class AssetVersion(Base):
    __tablename__ = "asset_versions"
    __table_args__ = (
        UniqueConstraint("asset_id", "version_number", name="uq_asset_versions_number"),
        CheckConstraint("version_number > 0", name="ck_asset_versions_number_positive"),
        CheckConstraint("length(btrim(title)) > 0", name="ck_asset_versions_title_nonempty"),
        CheckConstraint("length(btrim(created_by)) > 0", name="ck_asset_versions_created_by_nonempty"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[dict] = mapped_column(JSONB, nullable=False)
    model: Mapped[str | None] = mapped_column(String(120), nullable=True)
    prompt_version: Mapped[str | None] = mapped_column(String(80), nullable=True)
    created_by: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class AssetVersionSource(Base):
    __tablename__ = "asset_version_sources"
    __table_args__ = (
        CheckConstraint("length(btrim(excerpt)) > 0", name="ck_asset_version_sources_excerpt_nonempty"),
    )

    asset_version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("asset_versions.id", ondelete="CASCADE"), primary_key=True)
    interaction_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("interactions.id", ondelete="RESTRICT"), primary_key=True)
    excerpt: Mapped[str] = mapped_column(Text, primary_key=True)
