import json
import os
from pathlib import Path
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.crud.crud_book import book as book_crud
from app.schemas.book import BookCreate

def load_books_data() -> list:
    """Load books data from JSON file"""
    json_path = "data/books_seed.json"
    logger.info(f"Loading books data from: {json_path}")
    
    try:
        with open(json_path) as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Books data file not found: {json_path}")
        # Try alternative path
        alt_path = Path(__file__).parent.parent.parent / "data" / "books_seed.json"
        logger.info(f"Trying alternative path: {alt_path}")
        if alt_path.exists():
            with open(alt_path) as f:
                return json.load(f)
        raise

async def check_table_exists(db: AsyncSession, table_name: str) -> bool:
    """Check if a table exists in the database"""
    try:
        if os.getenv("DB_TYPE") == "postgres":
            query = text(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = :table_name)"
            )
        else:
            query = text(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=:table_name"
            )
        
        result = await db.execute(query, {"table_name": table_name})
        exists = result.scalar() is not None
        logger.info(f"Table '{table_name}' exists: {exists}")
        return exists
    except Exception as e:
        logger.warning(f"Error checking if table '{table_name}' exists: {e}")
        return False

async def init_db(db: AsyncSession) -> None:
    """Initialize database with seed data"""
    try:
        # First check if book table exists
        table_exists = await check_table_exists(db, "book")
        
        if not table_exists:
            logger.warning("Book table does not exist. Skipping data seeding.")
            return

        # Check if books already exist
        try:
            book_count = await book_crud.get_count(db)
            if book_count > 0:
                logger.info(f"Database already has {book_count} books. Skipping initial data load.")
                return
        except Exception as e:
            logger.warning(f"Error checking book count (tables might not be ready): {e}")
            return

        logger.info("Seeding initial book data...")
        books_data = load_books_data()

        books_created = 0
        for book_data in books_data:
            try:
                book_in = BookCreate(**book_data)
                await book_crud.create(db, obj_in=book_in)
                books_created += 1
                logger.debug(f"Successfully created book: {book_data['title']}")
            except Exception as e:
                logger.warning(f"Could not insert book '{book_data['title']}': {e}")
                # Continue with next book instead of failing completely
                continue
        
        logger.info(f"Successfully seeded {books_created} out of {len(books_data)} books.")
        
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")