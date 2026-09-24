import uuid
from datetime import datetime
from sqlalchemy import CheckConstraint, DateTime, Index, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Interaction(Base):
    __tablename__ = "interactions"
    __table_args__ = (
        UniqueConstraint("organization_id", "community_id", "external_id", name="uq_interactions_external_per_community"),
        UniqueConstraint("organization_id", "community_id", "fingerprint", name="uq_interactions_fingerprint_per_community"),
        CheckConstraint("length(btrim(organization_id)) > 0", name="ck_interactions_organization_nonempty"),
        CheckConstraint("length(btrim(community_id)) > 0", name="ck_interactions_community_nonempty"),
        CheckConstraint("length(btrim(author)) > 0", name="ck_interactions_author_nonempty"),
        CheckConstraint("length(btrim(channel)) > 0", name="ck_interactions_channel_nonempty"),
        CheckConstraint("length(btrim(type)) > 0", name="ck_interactions_type_nonempty"),
        CheckConstraint("length(btrim(text)) > 0", name="ck_interactions_text_nonempty"),
        CheckConstraint("external_id IS NULL OR length(btrim(external_id)) > 0", name="ck_interactions_external_nonempty"),
        CheckConstraint("fingerprint ~ '^[0-9a-f]{64}$'", name="ck_interactions_fingerprint_sha256"),
        Index("ix_interactions_community_created", "organization_id", "community_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[str] = mapped_column(String(100), nullable=False)
    community_id: Mapped[str] = mapped_column(String(100), nullable=False)
    external_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    author: Mapped[str] = mapped_column(String(200), nullable=False)
    channel: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[str] = mapped_column(String(100), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    occurred_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
