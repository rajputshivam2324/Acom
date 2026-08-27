"""
Service ORM model — represents a monitored microservice.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Float, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Service(Base):
    __tablename__ = "services"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(256), nullable=True)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="Healthy"
    )  # Healthy | Degraded | Critical | Maintenance
    latency_ms: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    cluster: Mapped[str] = mapped_column(String(128), nullable=False, default="cluster-us-east")
    uptime_pct: Mapped[float] = mapped_column(Float, nullable=False, default=99.99)
    service_type: Mapped[str] = mapped_column(
        String(64), nullable=False, default="Microservice"
    )  # Gateway | Microservice | Auth | Storage | Queue
    request_rate: Mapped[str] = mapped_column(String(32), nullable=True)  # e.g. "4.8k rpm"
    description: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    incidents = relationship("Incident", back_populates="service", lazy="selectin")
    telemetry_snapshots = relationship("TelemetrySnapshot", back_populates="service", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Service {self.name} [{self.status}]>"
