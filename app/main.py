from fastapi import FastAPI
from contextlib import asynccontextmanager
from loguru import logger
import subprocess
import asyncio

from app.api.v1.api import api_router
from app.core.config import settings
from app.db.init_db import init_db
from app.db.session import SessionLocal

async def run_migrations():
    """Run database migrations with better error handling"""
    try:
        logger.info("Running database migrations...")
        
        # Run alembic upgrade head
        result = subprocess.run(
            ["poetry", "run", "alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            timeout=30  # 30 second timeout
        )
        
        if result.returncode == 0:
            logger.info("✅ Database migrations completed successfully")
            return True
        else:
            logger.warning(f"⚠️ Database migrations failed: {result.stderr}")
            logger.info("Continuing without migrations...")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("❌ Database migrations timed out")
        return False
    except Exception as e:
        logger.error(f"❌ Error running migrations: {e}")
        return False

@asynccontextmanager
async def lifespan(app: FastAPI):
    # On startup
    logger.info("Starting up...")
    logger.info(f"Using {settings.DB_TYPE} database")
    
    # Run migrations (but don't fail startup if they fail)
    migration_success = await run_migrations()
    
    if not migration_success:
        logger.warning("Application starting without successful migrations")
    
    # Always try to seed data (init_db will check if tables exist)
    try:
        db = SessionLocal()
        await init_db(db)
        await db.close()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
    
    yield
    
    # On shutdown
    logger.info("Shutting down...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Book Recommendation System API"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
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