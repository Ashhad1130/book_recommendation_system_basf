import pytest
from app.db.models import Book, Review
from typing import List

@pytest.fixture
def mock_books_with_reviews() -> List[Book]:
    book1 = Book(
        id=1, 
        title="The Test Book", 
        author="Author A", 
        genre="Fiction", 
        reviews=[
            Review(id=1, rating=5, review_text="Excellent!", book_id=1, user_id=1),
            Review(id=2, rating=3, review_text="It was okay.", book_id=1, user_id=2),
        ]
    )
    book2 = Book(
        id=2, 
        title="Another Test", 
        author="Author B", 
        genre="Sci-Fi", 
        reviews=[
            Review(id=3, rating=1, review_text="Not for me.", book_id=2, user_id=1)
        ]
    )
    book3 = Book(
        id=3, 
        title="Empty Reviews", 
        author="Author C", 
        genre="Fantasy", 
        reviews=[]
    )
    return [book1, book2, book3]