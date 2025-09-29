from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query

from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.book import Book, BookWithReviews
from app.schemas.review import Review, ReviewCreate
from app.schemas.user import User
from app.api import deps
from app.services.book_service import book_service

router = APIRouter()

@router.get("/", response_model=List[Book])
async def read_books(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 10,
    search: Optional[str] = Query(None, min_length=2),
    current_user: User = Depends(deps.get_current_user),
):
    books = await book_service.get_books(db, skip=skip, limit=limit, search=search)
    return books

@router.post(
    "/{book_id}/reviews",
    response_model=Review,
    status_code=status.HTTP_201_CREATED
)
async def add_or_update_book_review(
    book_id: int,
    review_in: ReviewCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Add or update a review for a book.
    If the user already has a review for this book, it will be updated.
    """
    user_id = current_user.id
    review = await book_service.add_or_update_review(
        db, book_id=book_id, user_id=user_id, review_in=review_in
    )
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Book not found"
        )
    return review

# @router.put(
#     "/{book_id}/reviews",
#     response_model=Review
# )
# async def update_book_review(
#     book_id: int,
#     review_in: ReviewCreate,
#     db: AsyncSession = Depends(deps.get_db),
#     current_user: User = Depends(deps.get_current_user),
# ):
#     """
#     Update an existing review for a book.
#     Returns 404 if the user doesn't have an existing review.
#     """
#     user_id = current_user.id
    
#     # Check if review exists first
#     from app.crud.crud_review import review as review_crud
#     existing_review = await review_crud.get_by_book_and_user(
#         db, book_id=book_id, user_id=user_id
#     )
    
#     if not existing_review:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Review not found. Please create a review first."
#         )
    
#     # Update the review
#     review = await book_service.add_or_update_review(
#         db, book_id=book_id, user_id=user_id, review_in=review_in
#     )
    
#     return review

@router.get("/{book_id}/reviews", response_model=BookWithReviews)
async def get_book_reviews(
    book_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    book_with_reviews = await book_service.get_reviews_for_book(db, book_id=book_id)
    if not book_with_reviews:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Book not found"
        )
    return book_with_reviews

@router.delete("/{book_id}/reviews", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book_review(
    book_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Delete a user's review for a book
    """
    user_id = current_user.id
    deleted = await book_service.delete_review(
        db, book_id=book_id, user_id=user_id
    )
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    return None

@router.get("/{book_id}/reviews/me", response_model=Optional[Review])
async def get_my_review_for_book(
    book_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Get the current user's review for a specific book
    """
    from app.crud.crud_review import review as review_crud
    
    user_review = await review_crud.get_by_book_and_user(
        db, book_id=book_id, user_id=current_user.id
    )
    
    if user_review:
        return Review(
            id=user_review.id,
            rating=user_review.rating,
            review_text=user_review.review_text,
            book_id=user_review.book_id,
            user_id=user_review.user_id
        )
    return None