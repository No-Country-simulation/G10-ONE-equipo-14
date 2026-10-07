import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ApprovalRecord(Base):
    __tablename__ = "approvals"
    __table_args__ = (
        CheckConstraint("length(btrim(reviewer)) > 0", name="ck_approvals_reviewer_nonempty"),
        CheckConstraint("decision IN ('APPROVED', 'REJECTED')", name="ck_approvals_decision"),
        Index("ix_approvals_asset_created", "asset_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("assets.id", ondelete="RESTRICT"), nullable=False)
    asset_version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("asset_versions.id", ondelete="RESTRICT"), nullable=False)
    reviewer: Mapped[str] = mapped_column(String(200), nullable=False)
    decision: Mapped[str] = mapped_column(String(20), nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
