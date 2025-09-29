import json
import os
from pathlib import Path
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.crud_book import book as book_crud
from app.schemas.book import BookCreate

async def init_db(db: AsyncSession) -> None:
    try:
        # Try to check if books table exists and has data
        try:
            book_count = await book_crud.get_count(db)
            if book_count > 0:
                logger.info("Database already seeded. Skipping initial data load.")
                return
        except Exception as e:
            logger.warning(f"Could not check book count (tables might be empty): {e}")
            # Continue with seeding anyway

        logger.info("Seeding initial book data...")
        
        # Find and load the data file
        books_data = load_books_data()
        
        seeded_count = 0
        for book_data in books_data:
            try:
                book_in = BookCreate(**book_data)
                created_book = await book_crud.create(db, obj_in=book_in)
                seeded_count += 1
                logger.debug(f"Added book: {created_book.title}")
            except Exception as e:
                logger.warning(f"Could not insert book '{book_data.get('title', 'Unknown')}': {e}")
                continue
        
        logger.info(f"Successfully seeded {seeded_count} books.")
        
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
        logger.warning("Continuing without seeded data...")

def load_books_data():
    """Load books data from JSON file or return sample data"""
    try:
        # Try multiple possible locations for the data file
        possible_paths = [
            Path("../../data/book_seed.json"),
            Path("../data/books_seed.json"),
            Path("./data/books_seed.json"),
            Path(__file__).parent.parent.parent / "data" / "books_seed.json",
        ]
        
        data_file_path = None
        for path in possible_paths:
            if path.exists():
                data_file_path = path
                break
        
        if data_file_path:
            logger.info(f"Loading books data from: {data_file_path}")
            with open(data_file_path, "r") as f:
                return json.load(f)
        else:
            logger.warning("Books data file not found. Using sample data.")
            return get_sample_books_data()
            
    except Exception as e:
        logger.error(f"Error loading books data: {e}")
        logger.warning("Using sample data instead.")
        return get_sample_books_data()

def get_sample_books_data():
    """Return sample book data"""
    return [
        {
            "title": "The Hitchhiker's Guide to the Galaxy",
            "author": "Douglas Adams",
            "genre": "Science Fiction"
        },
        {
            "title": "Project Hail Mary",
            "author": "Andy Weir", 
            "genre": "Science Fiction"
        },
        {
            "title": "Dune",
            "author": "Frank Herbert",
            "genre": "Science Fiction"
        },
        {
            "title": "The Name of the Wind",
            "author": "Patrick Rothfuss",
            "genre": "Fantasy"
        },
        {
            "title": "1984",
            "author": "George Orwell",
            "genre": "Dystopian"
        },
        {
            "title": "Brave New World",
            "author": "Aldous Huxley",
            "genre": "Dystopian"
        },
        {
            "title": "Pride and Prejudice",
            "author": "Jane Austen",
            "genre": "Romance"
        }
    ]