from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.core.config import settings

def create_engine():
    """Create database engine based on DB_TYPE"""
    if settings.DB_TYPE == "sqlite":
        return create_async_engine(
            settings.SQLALCHEMY_DATABASE_URI,
            echo=True,
            poolclass=StaticPool,
            connect_args={"check_same_thread": False}
        )
    else:
        return create_async_engine(
            settings.SQLALCHEMY_DATABASE_URI,
            echo=True,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20
        )

engine = create_engine()
SessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)