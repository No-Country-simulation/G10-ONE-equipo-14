import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Opportunity(Base):
    __tablename__ = "opportunities"
    __table_args__ = (
        CheckConstraint("length(btrim(schema_version)) > 0", name="ck_opportunities_schema_version_nonempty"),
        CheckConstraint("length(btrim(kind)) > 0", name="ck_opportunities_kind_nonempty"),
        CheckConstraint("priority >= 0 AND priority <= 1", name="ck_opportunities_priority_range"),
        CheckConstraint("length(btrim(reason)) > 0", name="ck_opportunities_reason_nonempty"),
        CheckConstraint("status IN ('PENDING', 'REVIEW_REQUIRED', 'BLOCKED')", name="ck_opportunities_status"),
        Index("ix_opportunities_run_status_created", "run_id", "status", "created_at"),
        Index("ix_opportunities_analysis", "analysis_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("runs.id", ondelete="CASCADE"), nullable=False)
    analysis_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False)
    schema_version: Mapped[str] = mapped_column(String(20), nullable=False, default="v1")
    kind: Mapped[str] = mapped_column(String(60), nullable=False)
    priority: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class OpportunitySource(Base):
    __tablename__ = "opportunity_sources"

    opportunity_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("opportunities.id", ondelete="CASCADE"), primary_key=True)
    interaction_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("interactions.id", ondelete="RESTRICT"), primary_key=True)
