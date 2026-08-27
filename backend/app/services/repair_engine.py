"""
Repair Engine — handles approval workflow and simulated patch application.
"""
import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.repair_proposal import RepairProposal
from app.models.incident import Incident
from app.models.timeline_event import TimelineEvent

logger = logging.getLogger("acom.repair_engine")


async def approve_and_apply_repair(
    db: AsyncSession,
    repair_id,
    approved_by: str = "operator",
) -> Optional[dict]:
    """
    Approve a repair proposal and simulate applying the patch.
    In production, this would trigger a real CI/CD pipeline.
    """
    result = await db.execute(
        select(RepairProposal).where(RepairProposal.id == repair_id)
    )
    proposal = result.scalar_one_or_none()
    if not proposal:
        return None

    if proposal.status != "pending":
        return {"error": f"Proposal is already in '{proposal.status}' state"}

    # Mark as approved
    proposal.status = "approved"
    proposal.approved_by = approved_by
    await db.commit()

    # Add timeline event for approval
    event = TimelineEvent(
        incident_id=proposal.incident_id,
        event_type="Info",
        title=f"Repair approved by {approved_by}",
        description=f"Repair proposal '{proposal.title}' approved for application via CI/CD.",
    )
    db.add(event)
    await db.commit()

    # Simulate applying the patch (in production: trigger CI/CD)
    proposal.status = "applied"
    proposal.applied_at = datetime.now(timezone.utc)

    # Resolve the incident
    incident_result = await db.execute(
        select(Incident).where(Incident.id == proposal.incident_id)
    )
    incident = incident_result.scalar_one_or_none()

    if incident:
        incident.status = "Resolved"
        incident.pipeline_step = 6
        incident.resolved_at = datetime.now(timezone.utc)

        # Update service health
        if incident.service:
            incident.service.status = "Healthy"
            incident.service.latency_ms = 32.0

        # Add resolved timeline event
        resolved_event = TimelineEvent(
            incident_id=incident.id,
            event_type="Resolved",
            title=f"Incident {incident.incident_id} resolved",
            description=(
                f"Repair patch applied successfully. "
                f"Service restored to healthy state."
            ),
        )
        db.add(resolved_event)

    await db.commit()

    logger.info(f"Repair {repair_id} applied successfully for incident {incident.incident_id if incident else 'unknown'}")

    return {
        "repair_id": str(proposal.id),
        "status": proposal.status,
        "applied_at": proposal.applied_at.isoformat() if proposal.applied_at else None,
        "incident_status": incident.status if incident else None,
        "approved_by": approved_by,
    }


async def reject_repair(
    db: AsyncSession,
    repair_id,
) -> Optional[dict]:
    """Reject a repair proposal."""
    result = await db.execute(
        select(RepairProposal).where(RepairProposal.id == repair_id)
    )
    proposal = result.scalar_one_or_none()
    if not proposal:
        return None

    proposal.status = "rejected"

    event = TimelineEvent(
        incident_id=proposal.incident_id,
        event_type="Info",
        title="Repair proposal rejected",
        description=f"Repair proposal '{proposal.title}' was rejected by the operator.",
    )
    db.add(event)
    await db.commit()

    return {
        "repair_id": str(proposal.id),
        "status": "rejected",
    }
