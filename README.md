# Book Recommendation System - Backend API

This repository contains the source code for a simplified book recommendation system backend API, built with FastAPI. It demonstrates a clean, layered architecture and includes features like JWT authentication, a dynamic rating system, and background tasks with Celery.

## Architecture

The application follows a classic 3-layered architecture to separate concerns:

1.  **API Layer (`/app/api`)**: Handles HTTP requests and responses. It's responsible for data validation (via Pydantic schemas), routing, and dependency injection. It knows nothing about the database.

2.  **Service Layer (`/app/services`)**: Contains the core business logic. It orchestrates calls to the repository layer and performs any necessary computations (e.g., calculating average ratings). It is completely independent of the web framework.

3.  **Repository/Data Access Layer (`/app/crud`)**: This layer is responsible for all database interactions. It abstracts the database queries (using SQLAlchemy) and provides simple methods like `create`, `get`, `update` to the service layer.

This design makes the application highly testable and maintainable. For example, the service layer can be unit-tested by mocking the repository layer, without needing a real database.

---

## Features

-   **Framework**: FastAPI (fully asynchronous with `async`/`await`).
-   **Database**: SQLAlchemy ORM with support for both PostgreSQL (production/Docker) and SQLite (local development).
-   **Authentication**: JWT-based token authentication for protected endpoints.
-   **API Versioning**: All endpoints are prefixed with `/api/v1`.
-   **Dynamic Ratings**: Average book ratings are calculated on-the-fly.
-   **Search & Pagination**: The `/books` endpoint supports searching by title/author and `limit`/`offset` pagination.
-   **Background Tasks**: Celery is integrated to run tasks asynchronously (e.g., refreshing book data).
-   **Dependency Management**: Managed with Poetry.
-   **Containerization**: Fully containerized with `docker-compose` for easy setup.
-   **Migrations**: Alembic for handling database schema migrations.

---

## Setup and Run

You can run this project using either Docker (recommended) or a local Python 3.11 environment.

### 1. Using Docker (PostgreSQL)

This is the easiest way to get started.

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd book-recommendation-system
    ```

2.  **Create an environment file:**
    Copy the example file and update it if needed (the defaults work with `docker-compose`).
    ```bash
    cp .env.example .env
    ```

3.  **Build and run the services:**
    ```bash
    docker-compose up --build
    ```
4.  **Migrations (Alembic):**
    ```bash
    docker-compose exec app poetry run alembic revision --autogenerate -m "Intital Migrations"
    docker-compose exec app poetry run alembic upgrade head
    ```
5.  **Check Current Migrations:**
    ```bash
       docker-compose exec app poetry run alembic current 
    ```      

The API will be available at `http://localhost:8000/docs`. The database migrations are applied automatically on startup.

### 2. Local Environment (SQLite)

1.  **Prerequisites**: Python 3.11+ and Poetry.

2.  **Clone the repository and navigate into it.**

3.  **Install dependencies:**
    ```bash
    poetry install
    ```

4.  **Create an environment file:**
    Copy the example and make sure `DB_TYPE` is set to `sqlite`.
    ```bash
    cp .env.example .env
    # Open .env and set DB_TYPE=sqlite
    ```

5.  **Initialize the database:**
    For SQLite,Postgres, you would run migrations.
    ```bash
    # For Postgres, initialize alembic (only needs to be done once)
    # poetry run alembic init alembic
    # poetry run alembic revision --autogenerate -m "Initial migration"
    # poetry run alembic upgrade head
    ```

6.  **Run the application:**
    ```bash
    poetry run uvicorn app.main:app --reload
    ```
The API will be available at `http://localhost:8000/docs`.

---

## How to Run Tests

Tests are written with `pytest` and use fixtures for clean, reusable mock data.

1.  **Ensure dev dependencies are installed:**
    `poetry install` (if you haven't already).

2.  **Run the tests from the root directory:**
    ```bash
    poetry run pytest
    ```