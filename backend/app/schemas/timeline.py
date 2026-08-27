"""Pydantic schemas for TimelineEvent."""
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class TimelineEventCreate(BaseModel):
    event_type: str = "Info"
    title: str
    description: Optional[str] = None
    timestamp: Optional[datetime] = None


class TimelineEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    incident_id: uuid.UUID
    timestamp: datetime
    event_type: str
    title: str
    description: Optional[str] = None
