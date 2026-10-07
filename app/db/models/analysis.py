import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Analysis(Base):
    __tablename__ = "analyses"
    __table_args__ = (
        UniqueConstraint("run_id", "interaction_id", name="uq_analyses_run_interaction"),
        CheckConstraint("length(btrim(schema_version)) > 0", name="ck_analyses_schema_version_nonempty"),
        CheckConstraint("length(btrim(sentiment)) > 0", name="ck_analyses_sentiment_nonempty"),
        CheckConstraint("relevance >= 0 AND relevance <= 1", name="ck_analyses_relevance_range"),
        CheckConstraint("confidence >= 0 AND confidence <= 1", name="ck_analyses_confidence_range"),
        CheckConstraint("length(btrim(model)) > 0", name="ck_analyses_model_nonempty"),
        CheckConstraint("length(btrim(prompt_version)) > 0", name="ck_analyses_prompt_version_nonempty"),
        Index("ix_analyses_run_created", "run_id", "created_at"),
        Index("ix_analyses_interaction", "interaction_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("runs.id", ondelete="CASCADE"), nullable=False)
    interaction_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("interactions.id", ondelete="RESTRICT"), nullable=False)
    schema_version: Mapped[str] = mapped_column(String(20), nullable=False, default="v1")
    sentiment: Mapped[str] = mapped_column(String(40), nullable=False)
    topics: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    entities: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    relevance: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False)
    confidence: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False)
    model: Mapped[str] = mapped_column(String(120), nullable=False)
    prompt_version: Mapped[str] = mapped_column(String(80), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class AnalysisEvidence(Base):
    __tablename__ = "analysis_evidence"
    __table_args__ = (
        UniqueConstraint("analysis_id", "interaction_id", "excerpt", name="uq_analysis_evidence_source_excerpt"),
        CheckConstraint("length(btrim(excerpt)) > 0", name="ck_analysis_evidence_excerpt_nonempty"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False)
    interaction_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("interactions.id", ondelete="RESTRICT"), nullable=False)
    excerpt: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
