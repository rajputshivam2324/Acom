"""
AIConfig ORM model — singleton config for the AI provider used in investigations.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class AIConfig(Base):
    __tablename__ = "ai_config"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    provider: Mapped[str] = mapped_column(
        String(64), nullable=False, default="OpenAI (Standard)"
    )
    base_url: Mapped[str] = mapped_column(
        String(512), nullable=False, default="https://api.openai.com/v1"
    )
    api_key_encrypted: Mapped[str] = mapped_column(String(1024), nullable=True)
    default_model: Mapped[str] = mapped_column(
        String(128), nullable=False, default="gpt-4-turbo-preview"
    )
    system_prompt_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    system_prompt: Mapped[str] = mapped_column(
        Text,
        nullable=True,
        default="You are an expert SRE AI assistant. Analyze the provided logs and metrics to identify root causes...",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<AIConfig provider={self.provider} model={self.default_model}>"
