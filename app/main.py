from fastapi import FastAPI
from contextlib import asynccontextmanager
from loguru import logger

from app.api.v1.api import api_router
from app.core.config import settings
from app.db.init_db import init_db
from app.db.session import SessionLocal, engine
from app.db.base_class import Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    # On startup
    logger.info(f"Starting up with {settings.DB_TYPE} database...")
    logger.info(f"Database URI: {settings.SQLALCHEMY_DATABASE_URI}")
    
    # Create all database tables
    try:
        logger.info("Creating database tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully.")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        # Don't raise, continue startup
    
    # Seed initial data
    try:
        db = SessionLocal()
        await init_db(db)
        await db.close()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        # Don't raise, continue startup
    
    yield
    
    # On shutdown
    logger.info("Shutting down...")
    await engine.dispose()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "message": "Book Recommendation System API",
        "database": settings.DB_TYPE,
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint that verifies database connection"""
    try:
        async with SessionLocal() as db:
            from sqlalchemy import text
            await db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": settings.DB_TYPE,
            "connection": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": settings.DB_TYPE,
            "connection": "disconnected",
            "error": str(e)
        }

@app.get("/config/database")
async def get_database_config():
    """Endpoint to show current database configuration"""
    return {
        "db_type": settings.DB_TYPE,
        "database_uri": settings.SQLALCHEMY_DATABASE_URI.replace(settings.POSTGRES_PASSWORD, "***") if settings.DB_TYPE == "postgres" else settings.SQLALCHEMY_DATABASE_URI
    }