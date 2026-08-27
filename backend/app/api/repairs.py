"""
Repairs API — manage repair proposals, approve/reject/apply.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.incident import Incident
from app.models.repair_proposal import RepairProposal
from app.schemas.repair import RepairProposalOut, RepairAction
from app.services.repair_engine import approve_and_apply_repair, reject_repair

router = APIRouter(prefix="/api", tags=["Repairs"])


@router.get("/incidents/{incident_id}/repairs", response_model=List[RepairProposalOut])
async def get_repair_proposals(
    incident_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get all repair proposals for an incident."""
    inc_result = await db.execute(
        select(Incident).where(Incident.incident_id == incident_id)
    )
    incident = inc_result.scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")

    result = await db.execute(
        select(RepairProposal)
        .where(RepairProposal.incident_id == incident.id)
        .order_by(RepairProposal.created_at.desc())
    )
    return list(result.scalars().all())


@router.post("/repairs/{repair_id}/approve")
async def approve_repair(
    repair_id: str,
    body: RepairAction = RepairAction(),
    db: AsyncSession = Depends(get_db),
):
    """Approve and apply a repair proposal."""
    import uuid
    try:
        rid = uuid.UUID(repair_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid repair ID format")

    result = await approve_and_apply_repair(db, rid, body.approved_by or "operator")
    if not result:
        raise HTTPException(status_code=404, detail="Repair proposal not found")
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/repairs/{repair_id}/reject")
async def reject_repair_endpoint(
    repair_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Reject a repair proposal."""
    import uuid
    try:
        rid = uuid.UUID(repair_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid repair ID format")

    result = await reject_repair(db, rid)
    if not result:
        raise HTTPException(status_code=404, detail="Repair proposal not found")
    return result
