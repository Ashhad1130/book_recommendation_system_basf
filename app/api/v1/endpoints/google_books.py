from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional

from app.api import deps
from app.services.google_books_service import google_books_service
from app.schemas.google_books import GoogleBookSearchResponse, BookImportRequest, GoogleBookSearchResult
from app.crud.crud_book import book as book_crud
from app.schemas.book import Book, BookCreate
from app.schemas.user import User
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.get("/search", response_model=GoogleBookSearchResponse)
async def search_google_books(
    query: str = Query(..., min_length=2, description="Search query for books"),
    max_results: int = Query(10, ge=1, le=40, description="Maximum number of results"),
    current_user: User = Depends(deps.get_current_user),
):
    """Search books using Google Books API"""
    books = await google_books_service.search_books(query, max_results)
    
    return GoogleBookSearchResponse(
        books=books,
        total_results=len(books)
    )

@router.get("/{google_books_id}", response_model=GoogleBookSearchResult)
async def get_google_book_details(
    google_books_id: str,
    current_user: User = Depends(deps.get_current_user),
):
    """Get detailed information for a specific book from Google Books API"""
    book_details = await google_books_service.get_book_details(google_books_id)
    if not book_details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found in Google Books API"
        )
    return book_details

@router.post("/import", response_model=Book)
async def import_book_from_google(
    import_request: BookImportRequest,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Import a book from Google Books API into local database"""
    # Check if book already exists
    existing_book = await book_crud.get_by_google_books_id(db, google_books_id=import_request.google_books_id)
    if existing_book:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Book already exists in database"
        )
    
    # Get book details from Google Books API
    book_details = await google_books_service.get_book_details(import_request.google_books_id)
    if not book_details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found in Google Books API"
        )
    
    # Create book in local database
    book_create = BookCreate(
        title=book_details["title"],
        author=", ".join(book_details["authors"]),
        genre=import_request.genre,
        google_books_id=book_details["google_books_id"],
        isbn=book_details.get("isbn"),
        description=book_details.get("description"),
        page_count=book_details.get("page_count"),
        thumbnail_url=book_details.get("thumbnail")
    )
    
    book = await book_crud.create(db, obj_in=book_create)
    return book