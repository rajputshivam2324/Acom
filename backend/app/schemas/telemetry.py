"""Pydantic schemas for TelemetrySnapshot."""
import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class TelemetryIngest(BaseModel):
    service_name: str
    metric_type: str  # error_rate | latency_p99 | db_connections | cpu | memory
    value: float
    unit: Optional[str] = None
    timestamp: Optional[datetime] = None


class TelemetryBatchIngest(BaseModel):
    snapshots: List[TelemetryIngest]


class TelemetrySnapshotOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    service_id: uuid.UUID
    metric_type: str
    value: float
    unit: Optional[str] = None
    timestamp: datetime
