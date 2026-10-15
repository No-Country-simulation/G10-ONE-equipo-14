import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AlertRecord(Base):
    __tablename__ = "alerts"
    __table_args__ = (
        CheckConstraint("severity IN ('MEDIUM', 'HIGH')", name="ck_alerts_severity"),
        CheckConstraint("status IN ('OPEN', 'RESOLVED')", name="ck_alerts_status"),
        CheckConstraint("length(btrim(message)) > 0", name="ck_alerts_message_nonempty"),
        Index("ix_alerts_status_created", "status", "created_at"),
        Index("ix_alerts_run", "run_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("runs.id", ondelete="CASCADE"), nullable=False)
    interaction_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("interactions.id", ondelete="RESTRICT"), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default="HIGH")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="OPEN")
    message: Mapped[str] = mapped_column(Text, nullable=False)
    excerpt: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
