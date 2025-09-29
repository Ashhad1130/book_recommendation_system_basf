from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class ReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    review_text: Optional[str] = Field(None, max_length=5000)

class ReviewCreate(ReviewBase):
    pass

class Review(ReviewBase):
    id: int
    book_id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)