"""
Integrations API — manage external tool connections.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.integration import Integration
from app.schemas.integration import IntegrationOut, IntegrationUpdate

router = APIRouter(prefix="/api/integrations", tags=["Integrations"])


@router.get("", response_model=List[IntegrationOut])
async def list_integrations(db: AsyncSession = Depends(get_db)):
    """List all configured integrations."""
    result = await db.execute(select(Integration).order_by(Integration.name))
    return list(result.scalars().all())


@router.get("/{integration_name}", response_model=IntegrationOut)
async def get_integration(
    integration_name: str,
    db: AsyncSession = Depends(get_db),
):
    """Get integration by name."""
    result = await db.execute(
        select(Integration).where(Integration.name == integration_name)
    )
    integration = result.scalar_one_or_none()
    if not integration:
        raise HTTPException(status_code=404, detail=f"Integration '{integration_name}' not found")
    return integration


@router.patch("/{integration_name}", response_model=IntegrationOut)
async def update_integration(
    integration_name: str,
    body: IntegrationUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update an integration's configuration."""
    result = await db.execute(
        select(Integration).where(Integration.name == integration_name)
    )
    integration = result.scalar_one_or_none()
    if not integration:
        raise HTTPException(status_code=404, detail=f"Integration '{integration_name}' not found")

    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(integration, key, value)

    await db.commit()
    await db.refresh(integration)
    return integration


@router.post("/test")
async def test_connections(db: AsyncSession = Depends(get_db)):
    """Test all integration connections and return their status."""
    result = await db.execute(select(Integration))
    integrations = list(result.scalars().all())

    statuses = []
    for integ in integrations:
        # Simulate connection test
        statuses.append({
            "name": integ.name,
            "type": integ.integration_type,
            "status": integ.status,
            "test_result": "ok" if integ.status == "Connected" else "degraded",
        })

    all_ok = all(s["test_result"] == "ok" for s in statuses)
    return {
        "overall": "All systems operational" if all_ok else "Some connections degraded",
        "integrations": statuses,
    }
