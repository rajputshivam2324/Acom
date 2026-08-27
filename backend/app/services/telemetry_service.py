"""
Telemetry Service — generates and manages telemetry data.
"""
from datetime import datetime, timezone, timedelta
from typing import List, Optional
import random

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.telemetry_snapshot import TelemetrySnapshot
from app.models.service import Service


async def get_telemetry(
    db: AsyncSession,
    service_id,
    metric_type: Optional[str] = None,
    minutes: int = 15,
    limit: int = 100,
) -> List[TelemetrySnapshot]:
    """Get recent telemetry data for a service."""
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)
    query = (
        select(TelemetrySnapshot)
        .where(
            TelemetrySnapshot.service_id == service_id,
            TelemetrySnapshot.timestamp >= cutoff,
        )
        .order_by(TelemetrySnapshot.timestamp.desc())
        .limit(limit)
    )
    if metric_type:
        query = query.where(TelemetrySnapshot.metric_type == metric_type)

    result = await db.execute(query)
    return list(result.scalars().all())


async def ingest_telemetry(
    db: AsyncSession,
    service_name: str,
    metric_type: str,
    value: float,
    unit: Optional[str] = None,
    timestamp: Optional[datetime] = None,
) -> TelemetrySnapshot:
    """Ingest a single telemetry data point."""
    svc_result = await db.execute(
        select(Service).where(Service.name == service_name)
    )
    service = svc_result.scalar_one_or_none()
    if not service:
        raise ValueError(f"Service '{service_name}' not found")

    snapshot = TelemetrySnapshot(
        service_id=service.id,
        metric_type=metric_type,
        value=value,
        unit=unit,
        timestamp=timestamp or datetime.now(timezone.utc),
    )
    db.add(snapshot)
    await db.commit()
    await db.refresh(snapshot)
    return snapshot


async def generate_seed_telemetry(db: AsyncSession, service_name: str, is_critical: bool = False):
    """
    Generate simulated telemetry data points for a service.
    Used during seeding to populate realistic chart data.
    """
    svc_result = await db.execute(
        select(Service).where(Service.name == service_name)
    )
    service = svc_result.scalar_one_or_none()
    if not service:
        return

    now = datetime.now(timezone.utc)
    snapshots = []

    # Generate 15 minutes of data at 2-minute intervals
    for i in range(8):
        ts = now - timedelta(minutes=(14 - i * 2))
        is_anomaly = is_critical and i >= 5

        # Error rate
        error_rate = random.uniform(35.0, 40.0) if is_anomaly else random.uniform(0.8, 2.0)
        snapshots.append(TelemetrySnapshot(
            service_id=service.id,
            metric_type="error_rate",
            value=round(error_rate, 1),
            unit="%",
            timestamp=ts,
        ))

        # Latency p99
        latency = random.uniform(880, 950) if is_anomaly else random.uniform(100, 140)
        snapshots.append(TelemetrySnapshot(
            service_id=service.id,
            metric_type="latency_p99",
            value=round(latency, 0),
            unit="ms",
            timestamp=ts,
        ))

        # DB connections
        connections = random.uniform(240, 250) if is_anomaly else random.uniform(40, 55)
        snapshots.append(TelemetrySnapshot(
            service_id=service.id,
            metric_type="db_connections",
            value=round(connections, 0),
            unit="count",
            timestamp=ts,
        ))

    db.add_all(snapshots)
    await db.commit()
