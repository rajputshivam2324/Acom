"""
ACOM Backend — AI Disaster Recovery Commander

FastAPI application entry point with CORS, routing, and startup lifecycle.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.seed import seed_database

# Import all route modules
from app.api.incidents import router as incidents_router
from app.api.services import router as services_router
from app.api.timeline import router as timeline_router
from app.api.repairs import router as repairs_router
from app.api.integrations import router as integrations_router
from app.api.ai import router as ai_router
from app.api.telemetry import router as telemetry_router
from app.api.ws import router as ws_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)-24s | %(levelname)-5s | %(message)s",
)
logger = logging.getLogger("acom")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    # Startup
    logger.info("🚀 ACOM Backend starting up...")
    logger.info(f"   Environment: {settings.APP_ENV}")
    logger.info(f"   Database: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else 'configured'}")

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("   Database tables created/verified.")

    # Seed initial data
    await seed_database()
    logger.info("   Database seeded.")

    logger.info("✅ ACOM Backend ready!")
    yield

    # Shutdown
    logger.info("🛑 ACOM Backend shutting down...")
    await engine.dispose()


# ── FastAPI Application ──────────────────────────────────────────────────────
app = FastAPI(
    title="ACOM — AI Disaster Recovery Commander",
    description=(
        "Backend API for the AI Disaster Recovery Commander platform. "
        "Provides incident management, AI-powered root cause analysis, "
        "repair proposal workflow, service health monitoring, and real-time "
        "event streaming via WebSockets."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS Middleware ──────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register Routers ────────────────────────────────────────────────────────
app.include_router(incidents_router)
app.include_router(services_router)
app.include_router(timeline_router)
app.include_router(repairs_router)
app.include_router(integrations_router)
app.include_router(ai_router)
app.include_router(telemetry_router)
app.include_router(ws_router)


# ── Root & Health Endpoints ──────────────────────────────────────────────────
@app.get("/", tags=["Health"])
async def root():
    return {
        "name": "ACOM — AI Disaster Recovery Commander",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "environment": settings.APP_ENV,
        "database": "connected",
    }
