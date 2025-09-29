from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class GoogleBookSearchResult(BaseModel):
    google_books_id: str
    title: str
    authors: List[str]
    published_date: Optional[str] = None
    description: Optional[str] = None
    isbn: Optional[str] = None
    page_count: Optional[int] = None
    categories: List[str] = []
    average_rating: Optional[float] = None
    ratings_count: Optional[int] = None
    thumbnail: Optional[str] = None
    language: str = "en"

class GoogleBookSearchResponse(BaseModel):
    books: List[GoogleBookSearchResult]
    total_results: int

class BookImportRequest(BaseModel):
    google_books_id: str
    genre: str = Field(..., description="Genre to assign to the imported book")