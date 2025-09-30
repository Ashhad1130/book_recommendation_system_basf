from pydantic import BaseModel
from typing import List
from app.schemas.book import Book
from app.schemas.review import Review

class BookWithReviews(Book):
    reviews: List[Review] = []

    class Config:
        from_attributes = True