from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship  # Add this import
from sqlalchemy.sql import func
from app.db.base_class import Base

class Book(Base):
    __tablename__ = "book"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True, nullable=False)
    author = Column(String(255), index=True, nullable=False)
    genre = Column(String(100), nullable=False)
    google_books_id = Column(String(100), unique=True, index=True, nullable=True)
    isbn = Column(String(20), nullable=True)
    description = Column(Text, nullable=True)
    page_count = Column(Integer, nullable=True)
    thumbnail_url = Column(String(500), nullable=True)
    reviews = relationship("Review", back_populates="book", cascade="all, delete-orphan")

class Review(Base):
    __tablename__ = "review"
    id = Column(Integer, primary_key=True, index=True)
    rating = Column(Integer, nullable=False)
    review_text = Column(Text, nullable=True)
    book_id = Column(Integer, ForeignKey("book.id"), nullable=False)
    user_id = Column(Integer, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    book = relationship("Book", back_populates="reviews")