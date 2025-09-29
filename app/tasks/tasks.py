# app/tasks/tasks.py
import json
from celery import shared_task
from loguru import logger
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.schemas.book import BookCreate

@shared_task
def refresh_book_data_from_source():
    logger.info("Starting background task: Refreshing book data...")
    
    # Create sync database URL
    if settings.DB_TYPE == "postgres":
        sync_db_url = settings.SQLALCHEMY_DATABASE_URI.replace("+asyncpg", "")
    else:
        sync_db_url = settings.SQLALCHEMY_DATABASE_URI.replace("+aiosqlite", "")
        
    engine = create_engine(sync_db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    try:
        # Import models inside function to avoid circular imports
        from app.db.models import Book
        
        # Check if books already exist
        book_count = db.scalar(select(func.count()).select_from(Book))
        if book_count > 0:
            logger.info("Database already contains books. Skipping refresh.")
            return {"status": "skipped", "message": "Data already exists."}

        # Load and seed books
        with open("../../data/book_seed.json") as f:
            books_data = json.load(f)

        books_created = 0
        for book_data in books_data:
            book_in = BookCreate(**book_data)
            db_obj = Book(**book_in.model_dump())
            db.add(db_obj)
            books_created += 1
            
        db.commit()
        logger.info(f"Successfully seeded {books_created} books into the database.")
        return {"status": "success", "seeded_count": books_created}
        
    except Exception as e:
        logger.error(f"Error during book data refresh: {e}")
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()