import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch
from app.services.book_service import BookService
from app.schemas.review import ReviewCreate
from app.db.models import Review as ReviewModel

@pytest.mark.asyncio
async def test_review_update():
    """
    Test that a user can update their existing review
    """
    # 1. Arrange
    mock_db_session = AsyncMock()
    service = BookService()
    
    book_id = 1
    user_id = 1
    
    # Existing review data
    existing_review = ReviewModel(
        id=1,
        rating=4,
        review_text="Initial review",
        book_id=book_id,
        user_id=user_id
    )
    
    # Updated review data
    updated_review_data = ReviewCreate(
        rating=5,
        review_text="Updated review text"
    )
    
    # Mock the updated review
    updated_review = ReviewModel(
        id=1,  # Same ID - indicating update
        rating=5,
        review_text="Updated review text",
        book_id=book_id,
        user_id=user_id
    )
    
    # 2. Act - Mock the CRUD operations
    with patch('app.crud.crud_book.book.get', new_callable=AsyncMock) as mock_get_book:
        with patch('app.crud.crud_review.review.get_by_book_and_user', new_callable=AsyncMock) as mock_get_review:
            with patch('app.crud.crud_review.review.update', new_callable=AsyncMock) as mock_update:
                
                # Setup mocks
                mock_get_book.return_value = True  # Book exists
                mock_get_review.return_value = existing_review  # Review exists
                mock_update.return_value = updated_review  # Updated review
                
                # Call the service method
                result = await service.add_or_update_review(
                    db=mock_db_session,
                    book_id=book_id,
                    user_id=user_id,
                    review_in=updated_review_data
                )
    
    # 3. Assert
    assert result is not None
    assert result.id == 1  # Same ID means update, not create
    assert result.rating == 5  # Updated rating
    assert result.review_text == "Updated review text"  # Updated text
    assert result.user_id == user_id  # Same user
    assert result.book_id == book_id  # Same book

@pytest.mark.asyncio
async def test_review_create_when_none_exists():
    """
    Test that a new review is created when user doesn't have one
    """
    # 1. Arrange
    mock_db_session = AsyncMock()
    service = BookService()
    
    book_id = 1
    user_id = 1
    
    # New review data
    new_review_data = ReviewCreate(
        rating=4,
        review_text="New review"
    )
    
    # Mock the created review
    created_review = ReviewModel(
        id=2,  # New ID
        rating=4,
        review_text="New review",
        book_id=book_id,
        user_id=user_id
    )
    
    # 2. Act - Mock the CRUD operations
    with patch('app.crud.crud_book.book.get', new_callable=AsyncMock) as mock_get_book:
        with patch('app.crud.crud_review.review.get_by_book_and_user', new_callable=AsyncMock) as mock_get_review:
            with patch('app.crud.crud_review.review.create_with_user', new_callable=AsyncMock) as mock_create:
                
                # Setup mocks - no existing review
                mock_get_book.return_value = True  # Book exists
                mock_get_review.return_value = None  # No existing review
                mock_create.return_value = created_review  # New review created
                
                # Call the service method
                result = await service.add_or_update_review(
                    db=mock_db_session,
                    book_id=book_id,
                    user_id=user_id,
                    review_in=new_review_data
                )
    
    # 3. Assert
    assert result is not None
    assert result.id == 2  # New ID
    assert result.rating == 4
    assert result.review_text == "New review"

@pytest.mark.asyncio
async def test_multiple_users_can_review_same_book():
    """
    Test that multiple users can review the same book
    """
    # 1. Arrange
    mock_db_session = AsyncMock()
    service = BookService()
    
    book_id = 1
    user1_id = 1
    user2_id = 2
    
    # User 1 review data
    user1_review_data = ReviewCreate(
        rating=4,
        review_text="User 1 review"
    )
    
    # User 2 review data
    user2_review_data = ReviewCreate(
        rating=5,
        review_text="User 2 review"
    )
    
    # Mock reviews
    user1_review = ReviewModel(
        id=1,
        rating=4,
        review_text="User 1 review",
        book_id=book_id,
        user_id=user1_id
    )
    
    user2_review = ReviewModel(
        id=2,  # Different ID
        rating=5,
        review_text="User 2 review",
        book_id=book_id,
        user_id=user2_id
    )
    
    # 2. Act - Test user 1 creating review
    with patch('app.crud.crud_book.book.get', new_callable=AsyncMock) as mock_get_book:
        with patch('app.crud.crud_review.review.get_by_book_and_user', new_callable=AsyncMock) as mock_get_review:
            with patch('app.crud.crud_review.review.create_with_user', new_callable=AsyncMock) as mock_create:
                
                # User 1 - no existing review
                mock_get_book.return_value = True
                mock_get_review.return_value = None  # No existing review for user 1
                mock_create.return_value = user1_review
                
                result1 = await service.add_or_update_review(
                    db=mock_db_session,
                    book_id=book_id,
                    user_id=user1_id,
                    review_in=user1_review_data
                )
    
    # 3. Act - Test user 2 creating review
    with patch('app.crud.crud_book.book.get', new_callable=AsyncMock) as mock_get_book:
        with patch('app.crud.crud_review.review.get_by_book_and_user', new_callable=AsyncMock) as mock_get_review:
            with patch('app.crud.crud_review.review.create_with_user', new_callable=AsyncMock) as mock_create:
                
                # User 2 - no existing review
                mock_get_book.return_value = True
                mock_get_review.return_value = None  # No existing review for user 2
                mock_create.return_value = user2_review
                
                result2 = await service.add_or_update_review(
                    db=mock_db_session,
                    book_id=book_id,
                    user_id=user2_id,
                    review_in=user2_review_data
                )
    
    # 4. Assert
    assert result1 is not None
    assert result2 is not None
    assert result1.id != result2.id  # Different review IDs
    assert result1.user_id == user1_id
    assert result2.user_id == user2_id
    assert result1.book_id == book_id
    assert result2.book_id == book_id