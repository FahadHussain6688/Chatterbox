# API Documentation for My Chat App

## Authentication
Most endpoints require authentication. Use session authentication or add token authentication as needed.

---

## Status Endpoints

### List/Create Statuses
- **URL:** `/api/users/statuses/`
- **Methods:** GET, POST
- **Description:**
    - GET: List all statuses.
    - POST: Create a new status (authenticated users only).

#### Example Request (POST):
```
POST /api/users/statuses/
{
  "image": <file>
}
```

---

## Chat Endpoints

### List/Create Chats
- **URL:** `/api/chat/chats/`
- **Methods:** GET, POST
- **Description:**
    - GET: List all chats.
    - POST: Create a new chat.

### List/Create Messages in a Chat
- **URL:** `/api/chat/chats/<chat_id>/messages/`
- **Methods:** GET, POST
- **Description:**
    - GET: List all messages in a chat.
    - POST: Create a new message in a chat (authenticated users only).

#### Example Request (POST):
```
POST /api/chat/chats/1/messages/
{
  "content": "Hello!"
}
```

---

## Notes
- All endpoints return JSON.
- For file uploads, use multipart/form-data.
- Add authentication headers as needed.
