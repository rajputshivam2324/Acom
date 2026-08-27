"""Pydantic schemas for Service."""
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ServiceBase(BaseModel):
    name: str
    display_name: Optional[str] = None
    status: str = "Healthy"
    latency_ms: float = 0.0
    cluster: str = "cluster-us-east"
    uptime_pct: float = 99.99
    service_type: str = "Microservice"
    request_rate: Optional[str] = None
    description: Optional[str] = None


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    status: Optional[str] = None
    latency_ms: Optional[float] = None
    uptime_pct: Optional[float] = None
    request_rate: Optional[str] = None


class ServiceOut(ServiceBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
