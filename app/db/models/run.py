"""SQLAlchemy model for idempotent CommunityLab processing runs."""

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Index, JSON, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Run(Base):
    __tablename__ = "runs"
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "community_id",
            "idempotency_key",
            name="uq_runs_idempotency_per_community",
        ),
        CheckConstraint(
            "length(btrim(organization_id)) > 0",
            name="ck_runs_organization_nonempty",
        ),
        CheckConstraint(
            "length(btrim(community_id)) > 0",
            name="ck_runs_community_nonempty",
        ),
        CheckConstraint(
            "length(btrim(idempotency_key)) > 0",
            name="ck_runs_idempotency_key_nonempty",
        ),
        CheckConstraint(
            "request_hash ~ '^[0-9a-f]{64}$'",
            name="ck_runs_request_hash_sha256",
        ),
        Index(
            "ix_runs_community_created",
            "organization_id",
            "community_id",
            "created_at",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    organization_id: Mapped[str] = mapped_column(String(100), nullable=False)
    community_id: Mapped[str] = mapped_column(String(100), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(255), nullable=False)
    request_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
        default="PROCESSING",
    )
    response_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
