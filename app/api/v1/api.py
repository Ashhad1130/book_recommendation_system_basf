from fastapi import APIRouter
from .endpoints import auth, books, google_books

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(books.router, prefix="/books", tags=["books"])
api_router.include_router(google_books.router, prefix="/google-books", tags=["google-books"])