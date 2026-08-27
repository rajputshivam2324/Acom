"""
TimelineEvent ORM model — represents an event in the incident timeline.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class TimelineEvent(Base):
    __tablename__ = "timeline_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    incident_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("incidents.id"), nullable=False, index=True
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    event_type: Mapped[str] = mapped_column(
        String(32), nullable=False, default="Info"
    )  # Alert | Deploy | Maintenance | Info | AI | Resolved
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    # Relationships
    incident = relationship("Incident", back_populates="timeline_events")

    def __repr__(self) -> str:
        return f"<TimelineEvent [{self.event_type}] {self.title}>"
