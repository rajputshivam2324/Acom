"""Pydantic schemas for Incident."""
import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class IncidentBase(BaseModel):
    incident_id: str
    title: str
    severity: str = "SEV-3"
    status: str = "Detected"
    error_rate: Optional[float] = None
    p99_latency_ms: Optional[float] = None
    impacted_endpoint: Optional[str] = None


class IncidentCreate(IncidentBase):
    service_name: str  # Resolve to service_id on backend


class IncidentUpdate(BaseModel):
    status: Optional[str] = None
    pipeline_step: Optional[int] = None
    acknowledged: Optional[bool] = None
    acknowledged_by: Optional[str] = None
    error_rate: Optional[float] = None
    p99_latency_ms: Optional[float] = None
    root_cause_hypothesis: Optional[str] = None
    ai_confidence: Optional[float] = None
    correlated_pr: Optional[str] = None


class TimelineEventInline(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    timestamp: datetime
    event_type: str
    title: str
    description: Optional[str] = None


class InvestigationStepInline(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    step_order: int
    description: str
    status: str
    ai_output: Optional[str] = None


class RepairProposalInline(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    title: str
    description: str
    why: Optional[str] = None
    expected_result: Optional[str] = None
    risk_level: str
    patch_diff: Optional[str] = None
    status: str
    ai_confidence: Optional[float] = None
    created_at: datetime


class IncidentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    incident_id: str
    service_id: uuid.UUID
    title: str
    severity: str
    status: str
    pipeline_step: int
    error_rate: Optional[float] = None
    p99_latency_ms: Optional[float] = None
    impacted_endpoint: Optional[str] = None
    root_cause_hypothesis: Optional[str] = None
    ai_confidence: Optional[float] = None
    correlated_pr: Optional[str] = None
    acknowledged: bool
    acknowledged_by: Optional[str] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None
    updated_at: datetime


class IncidentDetail(IncidentOut):
    """Full incident detail with nested timeline, investigation steps, and repair proposals."""
    service_name: Optional[str] = None
    service_status: Optional[str] = None
    timeline_events: List[TimelineEventInline] = []
    investigation_steps: List[InvestigationStepInline] = []
    repair_proposals: List[RepairProposalInline] = []
