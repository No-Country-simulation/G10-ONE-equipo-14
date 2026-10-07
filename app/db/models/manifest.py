import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ManifestRecord(Base):
    __tablename__ = "manifests"
    __table_args__ = (
        UniqueConstraint("bucket", "object_key", name="uq_manifests_bucket_object_key"),
        CheckConstraint("length(btrim(schema_version)) > 0", name="ck_manifests_schema_version_nonempty"),
        CheckConstraint("length(btrim(bucket)) > 0", name="ck_manifests_bucket_nonempty"),
        CheckConstraint("length(btrim(object_key)) > 0", name="ck_manifests_object_key_nonempty"),
        CheckConstraint("length(btrim(content_type)) > 0", name="ck_manifests_content_type_nonempty"),
        CheckConstraint("sha256 ~ '^[0-9a-f]{64}$'", name="ck_manifests_sha256"),
        Index("ix_manifests_run", "run_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("runs.id", ondelete="RESTRICT"), nullable=False)
    asset_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("assets.id", ondelete="RESTRICT"), nullable=True)
    schema_version: Mapped[str] = mapped_column(String(20), nullable=False, default="v1")
    bucket: Mapped[str] = mapped_column(String(255), nullable=False)
    object_key: Mapped[str] = mapped_column(Text, nullable=False)
    content_type: Mapped[str] = mapped_column(String(150), nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    etag: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
