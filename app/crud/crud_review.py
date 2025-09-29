# app/crud/crud_review.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any

from .base import CRUDBase
from app.db.models import Review
from app.schemas.review import ReviewCreate

class CRUDReview(CRUDBase[Review, ReviewCreate, ReviewCreate]):
    async def create_with_user(
        self, db: AsyncSession, *, obj_in: ReviewCreate, user_id: int, book_id: int
    ) -> Review:
        db_obj = Review(**obj_in.model_dump(), user_id=user_id, book_id=book_id)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_by_book_and_user(
        self, db: AsyncSession, *, book_id: int, user_id: int
    ) -> Optional[Review]:
        result = await db.execute(
            select(self.model).filter(
                self.model.book_id == book_id, 
                self.model.user_id == user_id
            )
        )
        return result.scalars().first()

    async def get_reviews_by_book(
        self, db: AsyncSession, *, book_id: int
    ) -> list[Review]:
        result = await db.execute(
            select(self.model).filter(self.model.book_id == book_id)
        )
        return result.scalars().all()

    async def update_review(
        self, 
        db: AsyncSession, 
        *, 
        db_obj: Review, 
        obj_in: ReviewCreate
    ) -> Review:
        """Update a review with proper refresh"""
        update_data = obj_in.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

review = CRUDReview(Review)