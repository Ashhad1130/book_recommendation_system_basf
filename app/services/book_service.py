from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.crud_book import book as book_crud
from app.crud.crud_review import review as review_crud
from app.schemas.book import Book, BookWithReviews
from app.schemas.review import ReviewCreate, Review
from app.db.models import Book as BookModel

class BookService:
    def _calculate_average_rating(self, book_model: BookModel) -> float | None:
        if not book_model.reviews:
            return None
        return round(sum(r.rating for r in book_model.reviews) / len(book_model.reviews), 2)

    async def get_books(
        self, 
        db: AsyncSession, 
        *, 
        skip: int, 
        limit: int, 
        search: Optional[str]
    ) -> List[Book]:
        books_from_db = await book_crud.get_multi_with_reviews(
            db, skip=skip, limit=limit, search=search
        )
        
        books_with_avg_rating = []
        for book_model in books_from_db:
            avg_rating = self._calculate_average_rating(book_model)
            book_dict = {
                "id": book_model.id,
                "title": book_model.title,
                "author": book_model.author,
                "genre": book_model.genre,
                "average_rating": avg_rating,
                "google_books_id": book_model.google_books_id
            }
            books_with_avg_rating.append(Book(**book_dict))
            
        return books_with_avg_rating

    async def add_or_update_review(
        self, 
        db: AsyncSession, 
        *, 
        book_id: int, 
        user_id: int, 
        review_in: ReviewCreate
    ) -> Optional[Review]:
        # First check if book exists
        book_model = await book_crud.get(db, id=book_id)
        if not book_model:
            return None

        # Check if this user already has a review for this book
        existing_review = await review_crud.get_by_book_and_user(
            db, book_id=book_id, user_id=user_id
        )

        if existing_review:
            # UPDATE existing review
            print(f"Updating existing review ID {existing_review.id} by user {user_id} for book {book_id}")
            updated_review = await review_crud.update(
                db, db_obj=existing_review, obj_in=review_in
            )
            # Refresh to get the updated object
            await db.refresh(updated_review)
            return Review(
                id=updated_review.id,
                rating=updated_review.rating,
                review_text=updated_review.review_text,
                book_id=updated_review.book_id,
                user_id=updated_review.user_id
            )
        else:
            # CREATE new review
            print(f"Creating new review by user {user_id} for book {book_id}")
            new_review = await review_crud.create_with_user(
                db, obj_in=review_in, user_id=user_id, book_id=book_id
            )
            return Review(
                id=new_review.id,
                rating=new_review.rating,
                review_text=new_review.review_text,
                book_id=new_review.book_id,
                user_id=new_review.user_id
            )

    async def get_reviews_for_book(
        self, db: AsyncSession, *, book_id: int
    ) -> Optional[BookWithReviews]:
        book_model = await book_crud.get_with_reviews(db, id=book_id)
        if not book_model:
            return None
        
        avg_rating = self._calculate_average_rating(book_model)
        
        # Convert reviews to Review schema
        reviews = []
        for review_model in book_model.reviews:
            reviews.append(Review(
                id=review_model.id,
                rating=review_model.rating,
                review_text=review_model.review_text,
                book_id=review_model.book_id,
                user_id=review_model.user_id
            ))
        
        return BookWithReviews(
            id=book_model.id,
            title=book_model.title,
            author=book_model.author,
            genre=book_model.genre,
            average_rating=avg_rating,
            reviews=reviews
        )

    async def delete_review(
        self, 
        db: AsyncSession, 
        *, 
        book_id: int, 
        user_id: int
    ) -> bool:
        """Delete a user's review for a book"""
        existing_review = await review_crud.get_by_book_and_user(
            db, book_id=book_id, user_id=user_id
        )
        
        if existing_review:
            await review_crud.remove(db, id=existing_review.id)
            return True
        return False

book_service = BookService()