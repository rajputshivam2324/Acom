"""
AI Config API — manage AI provider settings.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.ai_config import AIConfig
from app.schemas.ai_config import AIConfigOut, AIConfigUpdate

router = APIRouter(prefix="/api/ai", tags=["AI Config"])


@router.get("/config", response_model=AIConfigOut)
async def get_ai_config(db: AsyncSession = Depends(get_db)):
    """Get the current AI provider configuration."""
    result = await db.execute(select(AIConfig).limit(1))
    config = result.scalar_one_or_none()
    if not config:
        # Create default config
        config = AIConfig()
        db.add(config)
        await db.commit()
        await db.refresh(config)
    return config


@router.put("/config", response_model=AIConfigOut)
async def update_ai_config(
    body: AIConfigUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update the AI provider configuration."""
    result = await db.execute(select(AIConfig).limit(1))
    config = result.scalar_one_or_none()
    if not config:
        config = AIConfig()
        db.add(config)

    updates = body.model_dump(exclude_unset=True)

    # Handle API key separately (encrypt in production)
    if "api_key" in updates:
        config.api_key_encrypted = updates.pop("api_key")

    for key, value in updates.items():
        if hasattr(config, key):
            setattr(config, key, value)

    await db.commit()
    await db.refresh(config)
    return config
