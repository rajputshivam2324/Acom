"""Pydantic schemas for Integration."""
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict


class IntegrationUpdate(BaseModel):
    status: Optional[str] = None
    endpoint_url: Optional[str] = None
    config_json: Optional[Dict[str, Any]] = None


class IntegrationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    integration_type: str
    status: str
    endpoint_url: Optional[str] = None
    description: Optional[str] = None
    config_json: Optional[Dict[str, Any]] = None
    icon_hint: Optional[str] = None
    created_at: datetime
    updated_at: datetime
