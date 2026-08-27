"""
Incidents API — CRUD, acknowledge, investigate, resolve.
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.incident import IncidentOut, IncidentCreate, IncidentUpdate, IncidentDetail
from app.services import incident_service
from app.services.ai_investigator import run_investigation

router = APIRouter(prefix="/api/incidents", tags=["Incidents"])


@router.get("", response_model=List[IncidentOut])
async def list_incidents(
    status: Optional[str] = Query(None, description="Filter by status"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List all incidents with optional filtering."""
    return await incident_service.list_incidents(db, status=status, severity=severity, limit=limit, offset=offset)


@router.get("/count")
async def get_incident_count(
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Get incident count."""
    count = await incident_service.get_incident_count(db, status=status)
    return {"count": count, "status_filter": status}


@router.get("/{incident_id}", response_model=IncidentDetail)
async def get_incident(
    incident_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get full incident detail including timeline, investigation steps, and repair proposals."""
    incident = await incident_service.get_incident(db, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")

    # Build the detail response
    return IncidentDetail(
        id=incident.id,
        incident_id=incident.incident_id,
        service_id=incident.service_id,
        title=incident.title,
        severity=incident.severity,
        status=incident.status,
        pipeline_step=incident.pipeline_step,
        error_rate=incident.error_rate,
        p99_latency_ms=incident.p99_latency_ms,
        impacted_endpoint=incident.impacted_endpoint,
        root_cause_hypothesis=incident.root_cause_hypothesis,
        ai_confidence=incident.ai_confidence,
        correlated_pr=incident.correlated_pr,
        acknowledged=incident.acknowledged,
        acknowledged_by=incident.acknowledged_by,
        created_at=incident.created_at,
        resolved_at=incident.resolved_at,
        updated_at=incident.updated_at,
        service_name=incident.service.name if incident.service else None,
        service_status=incident.service.status if incident.service else None,
        timeline_events=incident.timeline_events or [],
        investigation_steps=incident.investigation_steps or [],
        repair_proposals=incident.repair_proposals or [],
    )


@router.post("", response_model=IncidentOut, status_code=201)
async def create_incident(
    body: IncidentCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new incident."""
    try:
        incident = await incident_service.create_incident(
            db,
            incident_id=body.incident_id,
            service_name=body.service_name,
            title=body.title,
            severity=body.severity,
            error_rate=body.error_rate,
            p99_latency_ms=body.p99_latency_ms,
            impacted_endpoint=body.impacted_endpoint,
        )
        return incident
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{incident_id}", response_model=IncidentOut)
async def update_incident(
    incident_id: str,
    body: IncidentUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update an incident's fields."""
    incident = await incident_service.update_incident(
        db, incident_id, body.model_dump(exclude_unset=True)
    )
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
    return incident


@router.post("/{incident_id}/acknowledge", response_model=IncidentOut)
async def acknowledge_incident(
    incident_id: str,
    acknowledged_by: str = Query("operator"),
    db: AsyncSession = Depends(get_db),
):
    """Acknowledge an incident."""
    incident = await incident_service.acknowledge_incident(db, incident_id, acknowledged_by)
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
    return incident


@router.post("/{incident_id}/investigate")
async def investigate_incident(
    incident_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Trigger AI investigation for an incident."""
    incident = await incident_service.get_incident(db, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")

    if incident.status == "Resolved":
        raise HTTPException(status_code=400, detail="Cannot investigate a resolved incident")

    result = await run_investigation(db, incident)
    return result
