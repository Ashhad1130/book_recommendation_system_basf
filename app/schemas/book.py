from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from .review import Review

class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    author: str = Field(..., min_length=1, max_length=255)
    genre: str = Field(..., min_length=1, max_length=100)

class BookCreate(BookBase):
    pass

class Book(BookBase):
    id: int
    average_rating: Optional[float] = Field(None, ge=1, le=5)

    model_config = ConfigDict(from_attributes=True)

class BookWithReviews(Book):
    reviews: List[Review] = []

    model_config = ConfigDict(from_attributes=True)