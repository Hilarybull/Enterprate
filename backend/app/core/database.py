"""Database connection and utilities"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from app.core.config import settings
from typing import AsyncGenerator

# SQLAlchemy async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,  # Set to True for SQL query logging in development
    poolclass=NullPool,  # Disable connection pooling for development
    future=True
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database session.
    
    Usage in routes:
        async def my_route(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_db():
    """Initialize database connection (called on startup)"""
    # Import all models to ensure they are registered with SQLAlchemy
    from app.models import (
        User, Workspace, WorkspaceMembership, BusinessProfile,
        Project, Website, WebsitePage, Invoice, Lead, IntelligenceEvent
    )
    # In production, use Alembic migrations instead of create_all
    # from app.models.base import Base
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)
    pass

async def close_db():
    """Close database connection (called on shutdown)"""
    await engine.dispose()
