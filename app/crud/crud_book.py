from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from .base import CRUDBase
from app.db.models import Book
from app.schemas.book import BookCreate

class CRUDBook(CRUDBase[Book, BookCreate, None]):
    async def get_multi_with_reviews(
        self, 
        db: AsyncSession, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        search: Optional[str] = None
    ) -> List[Book]:
        query = select(self.model).options(selectinload(self.model.reviews)).offset(skip).limit(limit).order_by(self.model.id)
        if search:
            query = query.filter(
                (self.model.title.ilike(f"%{search}%")) |
                (self.model.author.ilike(f"%{search}%"))
            )
        result = await db.execute(query)
        return result.scalars().unique().all()

    async def get_with_reviews(self, db: AsyncSession, id: int) -> Optional[Book]:
        query = select(self.model).options(selectinload(self.model.reviews)).where(self.model.id == id)
        result = await db.execute(query)
        return result.scalars().first()

    async def get_by_google_books_id(self, db: AsyncSession, google_books_id: str) -> Optional[Book]:
        result = await db.execute(
            select(self.model).filter(self.model.google_books_id == google_books_id)
        )
        return result.scalars().first()

book = CRUDBook(Book)