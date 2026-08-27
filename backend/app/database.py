"""
SQLAlchemy async engine, session factory, and Base model.
Configured for Neon DB (serverless PostgreSQL) with SSL and connection pooling.
"""
import ssl
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.config import settings


# Neon DB requires SSL — asyncpg doesn't support sslmode= in the URL,
# so we pass it via connect_args
_connect_args = {}
if "neon.tech" in settings.DATABASE_URL or "neon" in settings.DATABASE_URL:
    # Create a permissive SSL context for Neon's pooler endpoint
    _ssl_context = ssl.create_default_context()
    _ssl_context.check_hostname = False
    _ssl_context.verify_mode = ssl.CERT_NONE
    _connect_args["ssl"] = _ssl_context

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=(settings.APP_ENV == "development"),
    pool_size=5,          # Neon pooler has its own limits; keep low
    max_overflow=5,
    pool_pre_ping=True,   # Detect dead connections from Neon scale-to-zero
    pool_recycle=300,      # Refresh connections every 5 min
    connect_args=_connect_args,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    """FastAPI dependency that yields an async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
