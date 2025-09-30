import json
import asyncio
from celery import shared_task
from celery.schedules import crontab
from loguru import logger
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.schemas.book import BookCreate
from typing import Optional

@shared_task
def refresh_book_data_from_google_books():
    """
    Background task to find books without a Google Books ID, search for them,
    and update them with the retrieved data.
    """
    logger.info("🎯 Starting enrichment task: Finding books WITHOUT Google Books data...")
    
    try:
        # Create sync database URL
        if settings.DB_TYPE == "postgres":
            sync_db_url = settings.SQLALCHEMY_DATABASE_URI.replace("+asyncpg", "+psycopg2")
        else:
            sync_db_url = settings.SQLALCHEMY_DATABASE_URI.replace("+aiosqlite", "")
            
        engine = create_engine(sync_db_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        db = SessionLocal()
        
        from app.db.models import Book
        from app.services.google_books_service import google_books_service

        books_to_enrich = db.execute(select(Book)).scalars().all()
        if not books_to_enrich:
            logger.info("✅ No books to enrich. All books already have Google Books IDs.")
            return {"status": "success", "message": "No books needed enrichment."}

        logger.info(f"📚 Found {len(books_to_enrich)} books WITHOUT Google Books ID to enrich.")

        # Process books
        books_enriched = 0
        books_failed = 0

        for book in books_to_enrich:
            try:
                logger.info(f"🔍 Searching Google Books for: '{book.title}' by {book.author}")
                
                # Search Google Books API
                search_query = f"{book.title} {book.author}"
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    # Search for the book
                    results = loop.run_until_complete(
                        google_books_service.search_books(query=search_query, max_results=3)
                    )
                    
                    if results and len(results) > 0:
                        # Take the first result as the best match
                        api_data = results[0]
                        
                        # Update the book with Google Books data
                        book.google_books_id = api_data.get("google_books_id")
                        book.description = api_data.get("description") or book.description
                        book.page_count = api_data.get("page_count") or book.page_count
                        book.thumbnail_url = api_data.get("thumbnail") or book.thumbnail_url
                        book.isbn = api_data.get("isbn") or book.isbn
                        
                        # Handle authors list
                        if api_data.get("authors"):
                            book.author = ", ".join(api_data["authors"])
                        
                        books_enriched += 1
                        logger.info(f"✅ Enriched: '{book.title}' with Google Books ID: {book.google_books_id}")
                    else:
                        logger.warning(f"⚠️ No Google Books match found for: '{book.title}'")
                        books_failed += 1
                        
                finally:
                    loop.close()
                    
            except Exception as e:
                logger.error(f"❌ Error enriching book '{book.title}': {e}")
                books_failed += 1
                continue

        # Commit all changes
        db.commit()

        result_summary = {
            "status": "success",
            "books_enriched": books_enriched,
            "books_failed": books_failed,
            "total_processed": len(books_to_enrich),
        }
        logger.info(f"✅ Book enrichment completed: {result_summary}")
        return result_summary

    except Exception as e:
        logger.error(f"❌ Critical error in enrichment task: {e}")
        if db:
            db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        if db:
            db.close()

@shared_task
def refresh_book_data_from_source():
    """
    Background task to refresh book data from the seed file
    This simulates refreshing from an external API
    """
    logger.info("🎯 Starting background task: Refreshing book data from seed file...")
    
    try:
        # Create sync database URL
        if settings.DB_TYPE == "postgres":
            sync_db_url = settings.SQLALCHEMY_DATABASE_URI.replace("+asyncpg", "+psycopg2")
        else:
            sync_db_url = settings.SQLALCHEMY_DATABASE_URI.replace("+aiosqlite", "")
            
        engine = create_engine(sync_db_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        db = SessionLocal()
        
        # Import models inside function to avoid circular imports
        from app.db.models import Book
        
        # Count existing books
        book_count = db.scalar(select(func.count()).select_from(Book))
        logger.info(f"📚 Found {book_count} existing books in database")
        
        # Load books from seed file
        with open("data/books_seed.json") as f:
            books_data = json.load(f)
        
        books_added = 0
        books_updated = 0
        
        for book_data in books_data:
            # Check if book already exists
            existing_book = db.scalar(
                select(Book).where(
                    (Book.title == book_data["title"]) & 
                    (Book.author == book_data["author"])
                )
            )
            
            if existing_book:
                # Update existing book
                existing_book.genre = book_data["genre"]
                books_updated += 1
                logger.debug(f"Updated book: {book_data['title']}")
            else:
                # Create new book
                book_in = BookCreate(**book_data)
                db_book = Book(**book_in.model_dump())
                db.add(db_book)
                books_added += 1
                logger.debug(f"Added new book: {book_data['title']}")
        
        db.commit()
        
        result = {
            "status": "success",
            "books_added": books_added,
            "books_updated": books_updated,
            "total_processed": len(books_data),
            "message": f"Successfully refreshed book data. Added: {books_added}, Updated: {books_updated}"
        }
        
        logger.info(f"✅ Book refresh completed: {result}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error during book data refresh: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

@shared_task
def calculate_book_statistics():
    """
    Background task to calculate book statistics
    """
    logger.info("📊 Starting background task: Calculating book statistics...")
    
    try:
        # Create sync database URL
        if settings.DB_TYPE == "postgres":
            sync_db_url = settings.SQLALCHEMY_DATABASE_URI.replace("+asyncpg", "+psycopg2")
        else:
            sync_db_url = settings.SQLALCHEMY_DATABASE_URI.replace("+aiosqlite", "")
            
        engine = create_engine(sync_db_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        db = SessionLocal()
        
        # Import models
        from app.db.models import Book, Review
        
        # Calculate statistics
        total_books = db.scalar(select(func.count()).select_from(Book))
        total_reviews = db.scalar(select(func.count()).select_from(Review))
        
        # Books with Google Books ID
        books_with_google_id = db.scalar(
            select(func.count()).select_from(Book).where(Book.google_books_id.isnot(None))
        )
        
        # Average rating per book
        books_with_reviews = db.scalar(
            select(func.count()).select_from(Book).where(Book.reviews.any())
        )
        
        # Genre distribution
        genre_stats = db.execute(
            select(Book.genre, func.count(Book.id))
            .group_by(Book.genre)
            .order_by(func.count(Book.id).desc())
        ).all()
        
        statistics = {
            "total_books": total_books,
            "total_reviews": total_reviews,
            "books_with_reviews": books_with_reviews,
            "books_without_reviews": total_books - books_with_reviews,
            "books_with_google_id": books_with_google_id,
            "books_without_google_id": total_books - books_with_google_id,
            "genre_distribution": {genre: count for genre, count in genre_stats},
            "average_reviews_per_book": round(total_reviews / total_books, 2) if total_books > 0 else 0
        }
        
        logger.info(f"✅ Statistics calculated: {statistics}")
        return statistics
        
    except Exception as e:
        logger.error(f"❌ Error calculating statistics: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

@shared_task
def send_new_book_notification(book_title: str, book_author: str):
    """
    Background task to simulate sending notifications about new books
    """
    logger.info(f"📢 Sending notification for new book: {book_title} by {book_author}")
    
    # Simulate some processing time
    import time
    time.sleep(2)
    
    # Simulate sending notification (email, push notification, etc.)
    notification_result = {
        "status": "sent",
        "book_title": book_title,
        "book_author": book_author,
        "message": f"Notification sent for '{book_title}' by {book_author}",
        "timestamp": time.time()
    }
    
    logger.info(f"✅ Notification sent: {notification_result}")
    return notification_result