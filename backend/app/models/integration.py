"""
Integration ORM model — external tool connections (GitHub, Prometheus, Loki, K8s).
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Integration(Base):
    __tablename__ = "integrations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    integration_type: Mapped[str] = mapped_column(
        String(64), nullable=False
    )  # scm | metrics | logs | orchestration | alerting | chat
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="Disconnected"
    )  # Connected | Degraded | Disconnected
    endpoint_url: Mapped[str] = mapped_column(String(512), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    config_json: Mapped[dict] = mapped_column(JSON, nullable=True, default=dict)
    icon_hint: Mapped[str] = mapped_column(String(64), nullable=True)  # For frontend icon mapping
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<Integration {self.name} [{self.status}]>"
