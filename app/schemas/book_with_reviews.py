from pydantic import BaseModel
from typing import List
from .book import Book
from .review import Review

class BookWithReviews(Book):
    reviews: List[Review] = []

    class Config:
        from_attributes = True