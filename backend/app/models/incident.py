"""
Incident ORM model — represents a production incident.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Float, DateTime, Text, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    incident_id: Mapped[str] = mapped_column(
        String(32), unique=True, nullable=False, index=True
    )  # e.g. INC-4821
    service_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("services.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    severity: Mapped[str] = mapped_column(
        String(16), nullable=False, default="SEV-3"
    )  # SEV-1 | SEV-2 | SEV-3 | SEV-4
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="Detected"
    )  # Detected | Investigating | Root Cause | Repair | Approval | Resolved
    pipeline_step: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    error_rate: Mapped[float] = mapped_column(Float, nullable=True)
    p99_latency_ms: Mapped[float] = mapped_column(Float, nullable=True)
    impacted_endpoint: Mapped[str] = mapped_column(String(512), nullable=True)
    root_cause_hypothesis: Mapped[str] = mapped_column(Text, nullable=True)
    ai_confidence: Mapped[float] = mapped_column(Float, nullable=True)  # 0.0 - 100.0
    correlated_pr: Mapped[str] = mapped_column(String(128), nullable=True)
    acknowledged: Mapped[bool] = mapped_column(default=False)
    acknowledged_by: Mapped[str] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    resolved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    service = relationship("Service", back_populates="incidents", lazy="selectin")
    timeline_events = relationship(
        "TimelineEvent", back_populates="incident", lazy="selectin",
        order_by="TimelineEvent.timestamp.desc()"
    )
    investigation_steps = relationship(
        "InvestigationStep", back_populates="incident", lazy="selectin",
        order_by="InvestigationStep.step_order"
    )
    repair_proposals = relationship(
        "RepairProposal", back_populates="incident", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Incident {self.incident_id} [{self.severity}] {self.status}>"
