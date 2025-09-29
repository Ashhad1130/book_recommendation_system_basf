import httpx
from typing import List, Optional, Dict, Any
from loguru import logger

class GoogleBooksService:
    def __init__(self):
        self.base_url = "https://www.googleapis.com/books/v1"
        self.api_key = None  # You can add API key if needed

    async def search_books(
        self, 
        query: str, 
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Search books using Google Books API"""
        try:
            async with httpx.AsyncClient() as client:
                params = {
                    "q": query,
                    "maxResults": max_results,
                    "printType": "books"
                }
                
                response = await client.get(f"{self.base_url}/volumes", params=params)
                response.raise_for_status()
                
                data = response.json()
                books = []
                
                for item in data.get("items", []):
                    volume_info = item.get("volumeInfo", {})
                    book_data = {
                        "google_books_id": item.get("id"),
                        "title": volume_info.get("title", "Unknown Title"),
                        "authors": volume_info.get("authors", ["Unknown Author"]),
                        "published_date": volume_info.get("publishedDate"),
                        "description": volume_info.get("description"),
                        "isbn": self._extract_isbn(volume_info.get("industryIdentifiers", [])),
                        "page_count": volume_info.get("pageCount"),
                        "categories": volume_info.get("categories", []),
                        "average_rating": volume_info.get("averageRating"),
                        "ratings_count": volume_info.get("ratingsCount"),
                        "thumbnail": volume_info.get("imageLinks", {}).get("thumbnail"),
                        "language": volume_info.get("language", "en")
                    }
                    books.append(book_data)
                
                return books
                
        except httpx.RequestError as e:
            logger.error(f"Google Books API request failed: {e}")
            return []
        except Exception as e:
            logger.error(f"Error processing Google Books API response: {e}")
            return []

    def _extract_isbn(self, industry_identifiers: List[Dict]) -> Optional[str]:
        """Extract ISBN from industry identifiers"""
        for identifier in industry_identifiers:
            if identifier.get("type") in ["ISBN_13", "ISBN_10"]:
                return identifier.get("identifier")
        return None

    async def get_book_details(self, google_books_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific book"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/volumes/{google_books_id}")
                response.raise_for_status()
                
                data = response.json()
                volume_info = data.get("volumeInfo", {})
                
                return {
                    "google_books_id": data.get("id"),
                    "title": volume_info.get("title", "Unknown Title"),
                    "authors": volume_info.get("authors", ["Unknown Author"]),
                    "published_date": volume_info.get("publishedDate"),
                    "description": volume_info.get("description"),
                    "isbn": self._extract_isbn(volume_info.get("industryIdentifiers", [])),
                    "page_count": volume_info.get("pageCount"),
                    "categories": volume_info.get("categories", []),
                    "average_rating": volume_info.get("averageRating"),
                    "ratings_count": volume_info.get("ratingsCount"),
                    "thumbnail": volume_info.get("imageLinks", {}).get("thumbnail"),
                    "language": volume_info.get("language", "en"),
                    "publisher": volume_info.get("publisher")
                }
                
        except httpx.RequestError as e:
            logger.error(f"Google Books API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Error processing Google Books API response: {e}")
            return None

google_books_service = GoogleBooksService()