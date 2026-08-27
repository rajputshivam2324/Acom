"""
Telemetry API — ingest and query telemetry data.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.service import Service
from app.schemas.telemetry import TelemetrySnapshotOut, TelemetryIngest
from app.services.telemetry_service import get_telemetry, ingest_telemetry

router = APIRouter(prefix="/api/telemetry", tags=["Telemetry"])


@router.get("/{service_name}", response_model=List[TelemetrySnapshotOut])
async def get_service_telemetry(
    service_name: str,
    metric_type: Optional[str] = Query(None),
    minutes: int = Query(15, ge=1, le=1440),
    db: AsyncSession = Depends(get_db),
):
    """Get recent telemetry data for a service."""
    svc_result = await db.execute(
        select(Service).where(Service.name == service_name)
    )
    service = svc_result.scalar_one_or_none()
    if not service:
        raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found")

    snapshots = await get_telemetry(db, service.id, metric_type=metric_type, minutes=minutes)
    return snapshots


@router.post("/ingest", response_model=TelemetrySnapshotOut, status_code=201)
async def ingest_telemetry_endpoint(
    body: TelemetryIngest,
    db: AsyncSession = Depends(get_db),
):
    """Ingest a single telemetry data point."""
    try:
        snapshot = await ingest_telemetry(
            db,
            service_name=body.service_name,
            metric_type=body.metric_type,
            value=body.value,
            unit=body.unit,
            timestamp=body.timestamp,
        )
        return snapshot
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
