import os
from pydantic_settings import BaseSettings
from typing import Literal

class Settings(BaseSettings):
    PROJECT_NAME: str = "Book Recommendation System"
    API_V1_STR: str = "/api/v1"
    
    # Database switch - change this to 'postgres' or 'sqlite'
    DB_TYPE: Literal["sqlite", "postgres"] = "sqlite"
    
    # PostgreSQL settings (used when DB_TYPE=postgres)
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "secret"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_DB: str = "bookrec"
    POSTGRES_PORT: str = "5432"
    
    # SQLite settings (used when DB_TYPE=sqlite)
    SQLITE_DB_PATH: str = "./book_recommendation.db"
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        if self.DB_TYPE == "postgres":
            return (
                f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
                f"{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        else:
            return f"sqlite+aiosqlite:///{self.SQLITE_DB_PATH}"

    SECRET_KEY: str = "your-super-secret-jwt-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    GOOGLE_BOOKS_API_KEY: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()