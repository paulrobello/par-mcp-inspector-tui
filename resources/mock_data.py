# Shared Mock Data for MCP Resource Testing
# Used by multiple resources for consistent test data

# Sample user database for Resource #2 (Dynamic User Info)
MOCK_USERS = {
    "123": {
        "user_id": "123",
        "name": "Alice Johnson",
        "email": "alice@example.com",
        "role": "admin",
        "status": "active",
        "created_at": "2024-01-15T10:30:00Z",
        "last_login": "2024-12-28T14:20:00Z",
        "preferences": {
            "theme": "dark",
            "notifications": True,
            "language": "en"
        }
    },
    "456": {
        "user_id": "456",
        "name": "Bob Smith",
        "email": "bob@example.com",
        "role": "user",
        "status": "active",
        "created_at": "2024-02-20T09:15:00Z",
        "last_login": "2024-12-27T16:45:00Z",
        "preferences": {
            "theme": "light",
            "notifications": False,
            "language": "es"
        }
    },
    "789": {
        "user_id": "789",
        "name": "Charlie Brown",
        "email": "charlie@example.com",
        "role": "user",
        "status": "suspended",
        "created_at": "2024-03-10T11:00:00Z",
        "last_login": "2024-12-20T08:30:00Z",
        "preferences": {
            "theme": "auto",
            "notifications": True,
            "language": "fr"
        }
    }
}