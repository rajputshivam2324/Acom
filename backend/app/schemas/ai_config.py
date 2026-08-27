"""Pydantic schemas for AIConfig."""
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class AIConfigUpdate(BaseModel):
    provider: Optional[str] = None
    base_url: Optional[str] = None
    api_key: Optional[str] = None  # Will be encrypted before storage
    default_model: Optional[str] = None
    system_prompt_enabled: Optional[bool] = None
    system_prompt: Optional[str] = None


class AIConfigOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    provider: str
    base_url: str
    default_model: str
    system_prompt_enabled: bool
    system_prompt: Optional[str] = None
    updated_at: datetime
    # NOTE: api_key_encrypted is never returned to the client
