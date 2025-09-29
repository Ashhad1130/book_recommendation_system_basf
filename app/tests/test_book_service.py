import pytest
from unittest.mock import AsyncMock, patch
from typing import List

from app.services.book_service import BookService
from app.db.models import Book

@pytest.mark.asyncio
async def test_get_books_calculates_average_rating(mock_books_with_reviews: List[Book]):
    """
    Test that the BookService correctly calculates the average rating.
    This test uses the 'mock_books_with_reviews' fixture for its data.
    """
    # 1. Arrange
    mock_db_session = AsyncMock()
    service = BookService()
    
    # 2. Act - Use patch to mock the CRUD function
    with patch('app.crud.crud_book.book.get_multi_with_reviews', 
               new_callable=AsyncMock) as mock_get_multi:
        mock_get_multi.return_value = mock_books_with_reviews
        
        result = await service.get_books(
            db=mock_db_session, skip=0, limit=10, search=None
        )

    # 3. Assert
    assert len(result) == 3
    assert result[0].id == 1
    assert result[0].average_rating == 4.0  # (5 + 3) / 2 = 4.0
    
    assert result[1].id == 2
    assert result[1].average_rating == 1.0  # Only one review of 1
    
    assert result[2].id == 3
    assert result[2].average_rating is None  # No reviews