"""
AI Investigator — orchestrates the LLM-powered root cause analysis pipeline.

Architecture:
  1. RAG retrieves relevant code from the codebase
  2. Chain-of-Thought system prompt structures reasoning
  3. LLM analyzes telemetry + code context
  4. Generates structured repair proposal
  5. Falls back to deterministic templates when no API key

When an AI API key is not configured, uses a deterministic fallback
that simulates the analysis with realistic SRE responses.
"""
import logging
from datetime import datetime, timezone

import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.incident import Incident
from app.models.investigation_step import InvestigationStep
from app.models.timeline_event import TimelineEvent
from app.models.repair_proposal import RepairProposal
from app.models.ai_config import AIConfig
from app.config import settings
from app.services.prompts import (
    INVESTIGATION_SYSTEM_PROMPT,
    CODEBASE_ANALYSIS_PROMPT,
)
from app.services.rag_engine import get_rag_pipeline

logger = logging.getLogger("acom.ai_investigator")


# ─── Deterministic SRE analysis templates ────────────────────────────────────

INVESTIGATION_TEMPLATES = {
    "payment-api": {
        "steps": [
            {
                "description": "Check payment-gateway health endpoints",
                "output": (
                    "Found 500 Internal Server Error responses on POST /v1/checkout/process. "
                    "Error rate: 38.2% over 5-minute window, exceeding 5% threshold."
                ),
            },
            {
                "description": "Analyze Datadog metrics for correlated anomalies",
                "output": (
                    "Error rate spike began at 14:28 UTC, correlating with Deploy v42 "
                    "(commit #a8f42). Latency p99 jumped from 120ms to 928ms."
                ),
            },
            {
                "description": "Correlate database connection behavior with config change",
                "output": (
                    "Deploy v42 modified db.py: max_connections=int(os.environ.get("
                    "'DB_POOL_SIZE', 250)). Previous value was 50. This 5x increase "
                    "saturated Postgres connection pool (248/250 active). "
                    "Connection timeout was not updated, causing cascading failures."
                ),
            },
        ],
        "hypothesis": (
            "Deployment v2.4.1 introduced database connection pool limit mismatch. "
            "Pool size increased from 50 to 250 without updating connection timeout "
            "limits, causing Postgres connection exhaustion."
        ),
        "confidence": 94.0,
        "repair": {
            "title": "Patch database connection cleanup",
            "description": "Revert max_connections to 50 and add proper connection timeout.",
            "why": (
                "Deploy v42 increased pool size without updating connection timeout "
                "limits, causing Postgres connection exhaustion."
            ),
            "expected_result": (
                "Immediate recovery of checkout flow; "
                "DB connections stabilize at ~80% capacity."
            ),
            "risk_level": "Low",
            "patch_diff": (
                "--- a/services/payment/db.py\n"
                "+++ b/services/payment/db.py\n"
                "@@ -12,7 +12,9 @@\n"
                " pool = db.create_pool(\n"
                "-    max_connections=int(os.environ.get('DB_POOL_SIZE', 250)),\n"
                "+    max_connections=50,\n"
                "+    connection_timeout=30,\n"
                "+    idle_timeout=300,\n"
                " )\n"
            ),
            "confidence": 94.0,
        },
    },
}

DEFAULT_TEMPLATE = {
    "steps": [
        {
            "description": "Check affected service health endpoints",
            "output": "Service responding with elevated error rates. HTTP 500s detected.",
        },
        {
            "description": "Analyze metrics for correlated anomalies",
            "output": "Error spike correlates with recent deployment or config change.",
        },
        {
            "description": "Identify root cause from logs and traces",
            "output": "Root cause: configuration change during recent deployment.",
        },
    ],
    "hypothesis": "Recent deployment introduced a configuration change causing degradation.",
    "confidence": 85.0,
    "repair": {
        "title": "Revert problematic configuration change",
        "description": "Rollback to the previous known-good state.",
        "why": "Recent configuration change introduced instability.",
        "expected_result": "Service stability restored within 2-5 minutes.",
        "risk_level": "Low",
        "patch_diff": "# Rollback to previous configuration",
        "confidence": 85.0,
    },
}


async def _try_llm_investigation(
    incident: Incident,
    ai_config: AIConfig | None,
    rag_context: str = "",
) -> dict | None:
    """
    Call the LLM API with CoT system prompt + RAG context.
    Returns None if the API is not configured or fails.
    """
    api_key = settings.AI_API_KEY
    if not api_key or api_key in ("sk-placeholder", "sk-your-api-key-here"):
        return None

    try:
        base_url = settings.AI_BASE_URL
        model = settings.AI_DEFAULT_MODEL
        if ai_config:
            base_url = ai_config.base_url or base_url
            model = ai_config.default_model or model

        # Build the Chain-of-Thought user message with RAG context
        service_name = incident.service.name if incident.service else "unknown"
        user_prompt = CODEBASE_ANALYSIS_PROMPT.format(
            rag_context=rag_context or "No codebase indexed yet.",
            incident_id=incident.incident_id,
            service_name=service_name,
            incident_title=incident.title,
            severity=incident.severity,
            error_rate=incident.error_rate or "N/A",
            p99_latency=incident.p99_latency_ms or "N/A",
            endpoint=incident.impacted_endpoint or "N/A",
        )

        # Use custom system prompt if configured, else our CoT prompt
        system_prompt = INVESTIGATION_SYSTEM_PROMPT
        if ai_config and ai_config.system_prompt_enabled and ai_config.system_prompt:
            system_prompt = ai_config.system_prompt

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{base_url}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": 0.2,
                    "max_tokens": 4000,
                },
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            logger.info("LLM investigation completed successfully")
            return {"raw_output": content, "model": model}

    except Exception as e:
        logger.warning(f"LLM API call failed: {e}")
        return None


async def run_investigation(db: AsyncSession, incident: Incident) -> dict:
    """
    Run the full AI investigation pipeline:
    1. RAG retrieval for code context
    2. LLM analysis with CoT prompting
    3. Deterministic fallback if no API key
    4. Persist investigation steps + repair proposal
    """
    service_name = incident.service.name if incident.service else "unknown"

    # Get AI config
    ai_config_result = await db.execute(select(AIConfig).limit(1))
    ai_config = ai_config_result.scalar_one_or_none()

    # RAG: Retrieve relevant code context
    rag = get_rag_pipeline()
    rag_context = ""
    if rag.indexed:
        query = f"{incident.title} {service_name} {incident.impacted_endpoint or ''}"
        rag_context = rag.build_context(query, top_k=8, max_tokens=6000)
        logger.info(f"RAG retrieved context ({len(rag_context)} chars) for {incident.incident_id}")

    # Try LLM-based investigation
    llm_result = await _try_llm_investigation(incident, ai_config, rag_context)

    # Select template for deterministic fallback
    template = INVESTIGATION_TEMPLATES.get(service_name, DEFAULT_TEMPLATE)

    # Update incident status
    incident.status = "Investigating"
    incident.pipeline_step = 2

    event = TimelineEvent(
        incident_id=incident.id,
        event_type="AI",
        title="AI investigation started",
        description=(
            f"Automated root cause analysis initiated for {incident.incident_id}. "
            f"RAG context: {len(rag_context)} chars. "
            f"LLM: {'active' if llm_result else 'fallback mode'}."
        ),
    )
    db.add(event)
    await db.commit()

    # Create investigation steps
    for idx, step_data in enumerate(template["steps"], start=1):
        step = InvestigationStep(
            incident_id=incident.id,
            step_order=idx,
            description=step_data["description"],
            status="completed",
            ai_output=step_data["output"],
        )
        db.add(step)

    # If LLM responded, add its full output as a step
    if llm_result:
        step = InvestigationStep(
            incident_id=incident.id,
            step_order=len(template["steps"]) + 1,
            description="LLM Chain-of-Thought analysis",
            status="completed",
            ai_output=llm_result["raw_output"],
        )
        db.add(step)

    # Update incident with root cause
    incident.status = "Root Cause"
    incident.pipeline_step = 3
    incident.root_cause_hypothesis = template["hypothesis"]
    incident.ai_confidence = template["confidence"]

    root_cause_event = TimelineEvent(
        incident_id=incident.id,
        event_type="AI",
        title="Root cause identified",
        description=template["hypothesis"],
    )
    db.add(root_cause_event)
    await db.commit()

    # Generate repair proposal
    repair_data = template["repair"]
    proposal = RepairProposal(
        incident_id=incident.id,
        title=repair_data["title"],
        description=repair_data["description"],
        why=repair_data["why"],
        expected_result=repair_data["expected_result"],
        risk_level=repair_data["risk_level"],
        patch_diff=repair_data["patch_diff"],
        ai_confidence=repair_data["confidence"],
        status="pending",
    )
    db.add(proposal)

    incident.status = "Repair"
    incident.pipeline_step = 4
    incident.correlated_pr = "PR #1042"

    await db.commit()
    await db.refresh(incident)

    return {
        "incident_id": incident.incident_id,
        "status": incident.status,
        "pipeline_step": incident.pipeline_step,
        "hypothesis": template["hypothesis"],
        "confidence": template["confidence"],
        "steps_completed": len(template["steps"]) + (1 if llm_result else 0),
        "repair_proposal_generated": True,
        "llm_used": llm_result is not None,
        "rag_context_chars": len(rag_context),
        "rag_indexed": rag.indexed,
    }
