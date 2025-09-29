# In-memory user database for demonstration
from app.core.security import get_password_hash

USERS_DB = {
    "testuser": {
        "id": 1,
        "username": "testuser",
        "hashed_password": get_password_hash("testpassword"),
    },
    "anotheruser": {
        "id": 2,
        "username": "anotheruser",
        "hashed_password": get_password_hash("anotherpassword"),
    },
    "ashhad": {
        "id": 3,
        "username": "ashhad",
        "hashed_password": get_password_hash("ashhadpassword"),
    },
}