"""
TelemetrySnapshot ORM model — time-series telemetry data points for services.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class TelemetrySnapshot(Base):
    __tablename__ = "telemetry_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    service_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("services.id"), nullable=False, index=True
    )
    metric_type: Mapped[str] = mapped_column(
        String(64), nullable=False
    )  # error_rate | latency_p99 | db_connections | cpu | memory | throughput
    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(16), nullable=True)  # %, ms, count, rpm
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    # Relationships
    service = relationship("Service", back_populates="telemetry_snapshots")

    def __repr__(self) -> str:
        return f"<TelemetrySnapshot {self.metric_type}={self.value}>"
