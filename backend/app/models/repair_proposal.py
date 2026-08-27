"""
RepairProposal ORM model — AI-generated repair suggestion requiring human approval.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Float, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class RepairProposal(Base):
    __tablename__ = "repair_proposals"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    incident_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("incidents.id"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    why: Mapped[str] = mapped_column(Text, nullable=True)
    expected_result: Mapped[str] = mapped_column(Text, nullable=True)
    risk_level: Mapped[str] = mapped_column(
        String(16), nullable=False, default="Medium"
    )  # Low | Medium | High | Critical
    patch_diff: Mapped[str] = mapped_column(Text, nullable=True)
    patch_file_path: Mapped[str] = mapped_column(String(512), nullable=True)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="pending"
    )  # pending | approved | applied | rejected | rolled_back
    ai_confidence: Mapped[float] = mapped_column(Float, nullable=True)
    approved_by: Mapped[str] = mapped_column(String(128), nullable=True)
    applied_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    incident = relationship("Incident", back_populates="repair_proposals")

    def __repr__(self) -> str:
        return f"<RepairProposal [{self.risk_level}] {self.title} ({self.status})>"
