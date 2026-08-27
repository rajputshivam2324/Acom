"""
Incident business logic — CRUD operations and lifecycle management.
"""
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.incident import Incident
from app.models.service import Service
from app.models.timeline_event import TimelineEvent


async def list_incidents(
    db: AsyncSession,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[Incident]:
    """List incidents with optional filtering."""
    query = select(Incident).options(
        selectinload(Incident.service)
    ).order_by(Incident.created_at.desc())

    if status:
        query = query.where(Incident.status == status)
    if severity:
        query = query.where(Incident.severity == severity)

    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_incident(db: AsyncSession, incident_id: str) -> Optional[Incident]:
    """Get a single incident by its human-readable ID (e.g., INC-4821)."""
    query = select(Incident).options(
        selectinload(Incident.service),
        selectinload(Incident.timeline_events),
        selectinload(Incident.investigation_steps),
        selectinload(Incident.repair_proposals),
    ).where(Incident.incident_id == incident_id)

    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_incident_by_uuid(db: AsyncSession, id: uuid.UUID) -> Optional[Incident]:
    """Get a single incident by its UUID."""
    query = select(Incident).options(
        selectinload(Incident.service),
        selectinload(Incident.timeline_events),
        selectinload(Incident.investigation_steps),
        selectinload(Incident.repair_proposals),
    ).where(Incident.id == id)

    result = await db.execute(query)
    return result.scalar_one_or_none()


async def create_incident(
    db: AsyncSession,
    incident_id: str,
    service_name: str,
    title: str,
    severity: str = "SEV-3",
    error_rate: float = None,
    p99_latency_ms: float = None,
    impacted_endpoint: str = None,
) -> Incident:
    """Create a new incident and add an initial timeline event."""
    # Resolve service
    svc_result = await db.execute(
        select(Service).where(Service.name == service_name)
    )
    service = svc_result.scalar_one_or_none()
    if not service:
        raise ValueError(f"Service '{service_name}' not found")

    incident = Incident(
        incident_id=incident_id,
        service_id=service.id,
        title=title,
        severity=severity,
        status="Detected",
        pipeline_step=1,
        error_rate=error_rate,
        p99_latency_ms=p99_latency_ms,
        impacted_endpoint=impacted_endpoint,
    )
    db.add(incident)
    await db.flush()

    # Auto-add detection timeline event
    event = TimelineEvent(
        incident_id=incident.id,
        event_type="Alert",
        title=f"Alert triggered: {title}",
        description=f"Incident {incident_id} detected on service {service_name}.",
    )
    db.add(event)
    await db.commit()
    await db.refresh(incident)
    return incident


async def update_incident(
    db: AsyncSession,
    incident_id: str,
    updates: dict,
) -> Optional[Incident]:
    """Update an incident's fields."""
    incident = await get_incident(db, incident_id)
    if not incident:
        return None

    for key, value in updates.items():
        if value is not None and hasattr(incident, key):
            setattr(incident, key, value)

    # Auto-resolve logic
    if updates.get("status") == "Resolved" and not incident.resolved_at:
        incident.resolved_at = datetime.now(timezone.utc)
        incident.pipeline_step = 6

        # Also update the service status back to Healthy
        if incident.service:
            incident.service.status = "Healthy"
            incident.service.latency_ms = 32.0

        # Add resolved timeline event
        event = TimelineEvent(
            incident_id=incident.id,
            event_type="Resolved",
            title=f"Incident {incident.incident_id} resolved",
            description="All systems have been restored to normal operation.",
        )
        db.add(event)

    await db.commit()
    await db.refresh(incident)
    return incident


async def acknowledge_incident(
    db: AsyncSession,
    incident_id: str,
    acknowledged_by: str = "operator",
) -> Optional[Incident]:
    """Acknowledge an incident."""
    incident = await get_incident(db, incident_id)
    if not incident:
        return None

    incident.acknowledged = True
    incident.acknowledged_by = acknowledged_by

    event = TimelineEvent(
        incident_id=incident.id,
        event_type="Info",
        title=f"Incident acknowledged by {acknowledged_by}",
        description=f"{acknowledged_by} acknowledged incident {incident.incident_id}.",
    )
    db.add(event)
    await db.commit()
    await db.refresh(incident)
    return incident


async def get_incident_count(db: AsyncSession, status: Optional[str] = None) -> int:
    """Count incidents, optionally filtered by status."""
    from sqlalchemy import func
    query = select(func.count(Incident.id))
    if status:
        query = query.where(Incident.status == status)
    result = await db.execute(query)
    return result.scalar_one()
