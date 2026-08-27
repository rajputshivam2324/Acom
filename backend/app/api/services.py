"""
Services API — list, detail, update service health.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.service import Service
from app.schemas.service import ServiceOut, ServiceCreate, ServiceUpdate

router = APIRouter(prefix="/api/services", tags=["Services"])


@router.get("", response_model=List[ServiceOut])
async def list_services(
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List all registered services."""
    query = select(Service).order_by(Service.name)
    if status:
        query = query.where(Service.status == status)
    result = await db.execute(query)
    return list(result.scalars().all())


@router.get("/health")
async def get_system_health(db: AsyncSession = Depends(get_db)):
    """Get aggregated system health overview."""
    result = await db.execute(select(Service))
    services = list(result.scalars().all())

    total = len(services)
    healthy = sum(1 for s in services if s.status == "Healthy")
    degraded = sum(1 for s in services if s.status == "Degraded")
    critical = sum(1 for s in services if s.status == "Critical")

    overall = "Healthy"
    if critical > 0:
        overall = "Degraded"
    elif degraded > 0:
        overall = "Degraded"

    return {
        "overall_status": overall,
        "total_services": total,
        "healthy": healthy,
        "degraded": degraded,
        "critical": critical,
        "operational_pct": round((healthy / total * 100) if total > 0 else 100, 1),
    }


@router.get("/{service_id}", response_model=ServiceOut)
async def get_service(
    service_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a service by UUID or name."""
    # Try by name first
    result = await db.execute(
        select(Service).where(Service.name == service_id)
    )
    service = result.scalar_one_or_none()

    if not service:
        # Try by UUID
        try:
            import uuid
            uid = uuid.UUID(service_id)
            result = await db.execute(
                select(Service).where(Service.id == uid)
            )
            service = result.scalar_one_or_none()
        except ValueError:
            pass

    if not service:
        raise HTTPException(status_code=404, detail=f"Service '{service_id}' not found")
    return service


@router.post("", response_model=ServiceOut, status_code=201)
async def create_service(
    body: ServiceCreate,
    db: AsyncSession = Depends(get_db),
):
    """Register a new service."""
    existing = await db.execute(
        select(Service).where(Service.name == body.name)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail=f"Service '{body.name}' already exists")

    service = Service(**body.model_dump())
    db.add(service)
    await db.commit()
    await db.refresh(service)
    return service


@router.patch("/{service_name}", response_model=ServiceOut)
async def update_service(
    service_name: str,
    body: ServiceUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a service's health status."""
    result = await db.execute(
        select(Service).where(Service.name == service_name)
    )
    service = result.scalar_one_or_none()
    if not service:
        raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found")

    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(service, key, value)

    await db.commit()
    await db.refresh(service)
    return service
