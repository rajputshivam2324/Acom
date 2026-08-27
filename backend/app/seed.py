"""
Database seeder — populates the database with realistic initial data
matching the frontend's hardcoded demonstration data.
"""
import asyncio
import logging
from datetime import datetime, timezone, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal, engine, Base
from app.models import (
    Service, Incident, TimelineEvent, InvestigationStep,
    RepairProposal, Integration, AIConfig, TelemetrySnapshot,
)
from app.services.telemetry_service import generate_seed_telemetry

logger = logging.getLogger("acom.seed")


async def seed_database():
    """Seed the database with initial data if empty."""
    async with AsyncSessionLocal() as db:
        # Check if already seeded
        result = await db.execute(select(Service).limit(1))
        if result.scalar_one_or_none():
            logger.info("Database already seeded, skipping.")
            return

        logger.info("Seeding database with initial data...")

        # ── Services ─────────────────────────────────────────────────────
        services = [
            Service(
                name="payment-api",
                display_name="Payment API",
                status="Critical",
                latency_ms=928.0,
                service_type="Microservice",
                request_rate="4.8k rpm",
                description="Handles payment processing and checkout flows.",
            ),
            Service(
                name="auth-service",
                display_name="Auth Service",
                status="Healthy",
                latency_ms=24.0,
                service_type="Auth",
                request_rate="8.1k rpm",
                description="Authentication and authorization service.",
            ),
            Service(
                name="user-db-cluster",
                display_name="User DB Cluster",
                status="Healthy",
                latency_ms=12.0,
                service_type="Storage",
                request_rate="2.4k rpm",
                description="Primary user database cluster (PostgreSQL).",
            ),
            Service(
                name="frontend-gateway",
                display_name="Frontend Gateway",
                status="Healthy",
                latency_ms=18.0,
                service_type="Gateway",
                request_rate="14.2k rpm",
                description="API gateway and reverse proxy for frontend clients.",
            ),
        ]
        db.add_all(services)
        await db.flush()

        # ── Active Incident (INC-4821) ───────────────────────────────────
        now = datetime.now(timezone.utc)
        payment_service = services[0]

        incident_4821 = Incident(
            incident_id="INC-4821",
            service_id=payment_service.id,
            title="Payment API Outage",
            severity="SEV-1",
            status="Investigating",
            pipeline_step=2,
            error_rate=38.2,
            p99_latency_ms=928.0,
            impacted_endpoint="POST /v1/checkout/process",
            created_at=now - timedelta(minutes=14),
        )
        db.add(incident_4821)
        await db.flush()

        # Timeline events for INC-4821
        timeline_events = [
            TimelineEvent(
                incident_id=incident_4821.id,
                timestamp=now - timedelta(minutes=14),
                event_type="Alert",
                title="Alert triggered: High Error Rate",
                description="Payment API error rate exceeded 20% threshold over 5m window.",
            ),
            TimelineEvent(
                incident_id=incident_4821.id,
                timestamp=now - timedelta(minutes=18),
                event_type="Deploy",
                title="Deploy started: Payment Service v2.4.1",
                description="Automated deployment initiated by CI/CD pipeline (commit #a8f42).",
            ),
            TimelineEvent(
                incident_id=incident_4821.id,
                timestamp=now - timedelta(minutes=31),
                event_type="Maintenance",
                title="Database Maintenance (Routine)",
                description="Scheduled vacuum operation completed successfully.",
            ),
        ]
        db.add_all(timeline_events)

        # ── Resolved Incident (INC-4820) ─────────────────────────────────
        incident_4820 = Incident(
            incident_id="INC-4820",
            service_id=payment_service.id,
            title="Stripe webhook parsing failure on recurring subscriptions",
            severity="SEV-2",
            status="Resolved",
            pipeline_step=6,
            error_rate=12.5,
            p99_latency_ms=450.0,
            impacted_endpoint="POST /v1/webhooks/stripe",
            root_cause_hypothesis="JSON payload schema change in Stripe API header v2026-06.",
            ai_confidence=98.0,
            correlated_pr="PR #1038",
            acknowledged=True,
            created_at=now - timedelta(hours=3),
            resolved_at=now - timedelta(hours=2),
        )
        db.add(incident_4820)
        await db.flush()

        # ── Resolved Incident (INC-4819) ─────────────────────────────────
        db_service = services[2]
        incident_4819 = Incident(
            incident_id="INC-4819",
            service_id=db_service.id,
            title="CPU spike causing read timeouts on secondary replica",
            severity="SEV-3",
            status="Resolved",
            pipeline_step=6,
            error_rate=5.2,
            p99_latency_ms=320.0,
            impacted_endpoint="GET /v1/users/*",
            root_cause_hypothesis="Unindexed query on user_sessions table after reporting job start.",
            ai_confidence=99.0,
            correlated_pr="PR #1031",
            acknowledged=True,
            created_at=now - timedelta(hours=6),
            resolved_at=now - timedelta(hours=5),
        )
        db.add(incident_4819)

        # ── Integrations ─────────────────────────────────────────────────
        integrations = [
            Integration(
                name="GitHub",
                integration_type="scm",
                status="Connected",
                endpoint_url="https://api.github.com",
                description="Source code, PRs, and commit history for root cause analysis.",
                config_json={"org": "sre-commander"},
                icon_hint="git-branch",
            ),
            Integration(
                name="Prometheus",
                integration_type="metrics",
                status="Connected",
                endpoint_url="http://prometheus:9090/api/v1/query",
                description="Metrics and alerting infrastructure integration.",
                config_json={"scrape_interval": "15s"},
                icon_hint="activity",
            ),
            Integration(
                name="Loki",
                integration_type="logs",
                status="Connected",
                endpoint_url="http://loki:3100",
                description="Log aggregation and stream analysis for AI context.",
                config_json={"retention": "30d"},
                icon_hint="file-text",
            ),
            Integration(
                name="Kubernetes",
                integration_type="orchestration",
                status="Degraded",
                endpoint_url="https://k8s-api.internal:6443",
                description="Cluster state, pod events, and deployment tracking.",
                config_json={"cluster": "prod-us-east", "token_expiry": "2026-08-28"},
                icon_hint="boxes",
            ),
        ]
        db.add_all(integrations)

        # ── AI Config ────────────────────────────────────────────────────
        ai_config = AIConfig(
            provider="OpenAI (Standard)",
            base_url="https://api.openai.com/v1",
            default_model="gpt-4-turbo-preview",
            system_prompt_enabled=True,
            system_prompt="You are an expert SRE AI assistant. Analyze the provided logs and metrics to identify root causes...",
        )
        db.add(ai_config)

        await db.commit()

        # ── Seed Telemetry Data ──────────────────────────────────────────
        await generate_seed_telemetry(db, "payment-api", is_critical=True)
        await generate_seed_telemetry(db, "auth-service", is_critical=False)
        await generate_seed_telemetry(db, "user-db-cluster", is_critical=False)
        await generate_seed_telemetry(db, "frontend-gateway", is_critical=False)

        logger.info("Database seeded successfully!")


async def create_tables():
    """Create all database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(create_tables())
    asyncio.run(seed_database())
