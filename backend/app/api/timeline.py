"""
Timeline API — get and add timeline events for an incident.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.incident import Incident
from app.models.timeline_event import TimelineEvent
from app.schemas.timeline import TimelineEventOut, TimelineEventCreate

router = APIRouter(prefix="/api/incidents", tags=["Timeline"])


@router.get("/{incident_id}/timeline", response_model=List[TimelineEventOut])
async def get_timeline(
    incident_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get the timeline events for an incident."""
    inc_result = await db.execute(
        select(Incident).where(Incident.incident_id == incident_id)
    )
    incident = inc_result.scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")

    result = await db.execute(
        select(TimelineEvent)
        .where(TimelineEvent.incident_id == incident.id)
        .order_by(TimelineEvent.timestamp.desc())
    )
    return list(result.scalars().all())


@router.post("/{incident_id}/timeline", response_model=TimelineEventOut, status_code=201)
async def add_timeline_event(
    incident_id: str,
    body: TimelineEventCreate,
    db: AsyncSession = Depends(get_db),
):
    """Add a new timeline event to an incident."""
    inc_result = await db.execute(
        select(Incident).where(Incident.incident_id == incident_id)
    )
    incident = inc_result.scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")

    event = TimelineEvent(
        incident_id=incident.id,
        event_type=body.event_type,
        title=body.title,
        description=body.description,
    )
    if body.timestamp:
        event.timestamp = body.timestamp

    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event
