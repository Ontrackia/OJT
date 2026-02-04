"""
Database Configuration for OnTrackIA OJT V2.0
PostgreSQL with async support for production-grade persistence
"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.exc import OperationalError
from typing import Generator
import os
import logging

logger = logging.getLogger(__name__)

# ==========================================
# DATABASE URL CONFIGURATION
# ==========================================

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    if os.getenv("ENVIRONMENT") == "production":
        raise RuntimeError("❌ DATABASE_URL must be set in production environment")
    # Development fallback
    DATABASE_URL = "postgresql://ontrackia_ojt:password@localhost:5432/ontrackia_ojt_db"

logger.info(f"🔌 Database URL: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'SQLite'}")

# ==========================================
# SYNC ENGINE (for migrations & scripts)
# ==========================================

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False
    )
else:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Detect dead connections
        pool_size=10,
        max_overflow=20,
        pool_recycle=300,  # Recycle connections every 5 min
        connect_args={"connect_timeout": 10},
        echo=False
    )

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# ==========================================
# ASYNC ENGINE (for FastAPI endpoints)
# ==========================================

ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
if ASYNC_DATABASE_URL.startswith("sqlite"):
    ASYNC_DATABASE_URL = ASYNC_DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://")

async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,
    pool_pre_ping=True
)

AsyncSessionLocal = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# ==========================================
# DEPENDENCY INJECTION
# ==========================================

def get_db() -> Generator[Session, None, None]:
    """
    Sync database session dependency.
    Used for scripts and migrations.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> Generator[AsyncSession, None, None]:
    """
    Async database session dependency.
    Used for FastAPI endpoints.
    """
    async with AsyncSessionLocal() as session:
        yield session


# ==========================================
# TENANT CONTEXT (for RLS)
# ==========================================

def set_tenant_context(db: Session, organization_id: int):
    """
    Set organization context for Row-Level Security.
    Future-proofing for multi-tenant architecture.
    """
    from sqlalchemy import text
    db.execute(text("SELECT set_config('app.organization_id', :org_id, FALSE)"), {"org_id": str(organization_id)})


# ==========================================
# DATABASE INITIALIZATION
# ==========================================

def init_db():
    """
    Initialize database - create all tables.
    Import all models here so they are registered.
    """
    # Import models to register them with Base.metadata
    from app.models import sms_models, audit_models, security_models
    
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database initialized successfully")


def drop_db():
    """
    Drop all tables (use with EXTREME caution!)
    """
    Base.metadata.drop_all(bind=engine)
    logger.warning("⚠️  All tables dropped")
