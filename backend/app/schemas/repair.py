"""Pydantic schemas for RepairProposal."""
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class RepairProposalCreate(BaseModel):
    title: str
    description: str
    why: Optional[str] = None
    expected_result: Optional[str] = None
    risk_level: str = "Medium"
    patch_diff: Optional[str] = None
    patch_file_path: Optional[str] = None
    ai_confidence: Optional[float] = None


class RepairAction(BaseModel):
    """Used for approve/reject actions."""
    approved_by: Optional[str] = "operator"


class RepairProposalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    incident_id: uuid.UUID
    title: str
    description: str
    why: Optional[str] = None
    expected_result: Optional[str] = None
    risk_level: str
    patch_diff: Optional[str] = None
    patch_file_path: Optional[str] = None
    status: str
    ai_confidence: Optional[float] = None
    approved_by: Optional[str] = None
    applied_at: Optional[datetime] = None
    created_at: datetime
