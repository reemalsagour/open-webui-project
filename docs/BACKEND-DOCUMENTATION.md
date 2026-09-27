# Internal AI Chat Platform — Backend API

Backend API documentation for the frontend.

**Backend:** FastAPI
**Authentication:** JWT Bearer Token
**Database:** PostgreSQL
**AI / Files / Knowledge:** Open WebUI API

# 0. Backend Setup

Follow these steps to run the backend using Docker Compose.

## 0.1 Create the `.env` File

Copy `.env.example` and rename the copy to:

```text
.env
```

Open `.env` and fill in the values that need to be:

Instructions for obtaining these values are provided in the backend documentation [Environment Variables](#10-environment-variables) section .

---

## 0.2 Open the Docker Directory

Open a terminal and navigate to the project's `docker` directory:

```bash
cd docker
```

---

## 0.3 Start the Docker Services

Start the dev docker backend, PostgreSQL, and Open WebUI services for local development:

```bash
docker compose --env-file "../.env"  -f docker-compose.yml -f docker-compose.dev.yml up --build -d
```

The `-d` option runs the containers in the background.

---

## 0.4 Sample Login Credentials

The seed creates the following sample user among others:

```text
Username: fatimah
Password: password
```

These credentials can be used to test the authentication and chat functionality.

---

## 0.5 Test the Backend

Open the FastAPI Swagger documentation in your browser:

```text
http://localhost:8000/docs
```

1. Click **Authorize**.
2. Enter the seeded username and password.
3. Authenticate.
4. Try some of the available routes, such as:

   * Authentication
   * Chats
   * Documents
   * Knowledge Bases
   * Open WebUI
5. Test a chat request to verify that the backend can communicate with Open WebUI and the configured AI model.

If the Swagger page loads and the routes respond successfully, the backend is running correctly.

## Backend Docker Setup Summary

```text
.env
  │
  ▼
docker compose up -d
  │
  ├── PostgreSQL
  ├── Open WebUI
  └── FastAPI Backend
          │
          ▼
   http://localhost:8000/docs
```

---

# 1. Base URL

During local development:

```text
http://localhost:8000
```

The frontend should communicate **only with the FastAPI backend**.

```text
Frontend → FastAPI → Open WebUI → Gemini
```

The frontend does **not** need to call Open WebUI directly.

---

# 2. Authentication

After logging in, the backend returns a JWT access token.

For protected endpoints, send:

```http
Authorization: Bearer <access_token>
```

Example:

```http
Authorization: Bearer eyJhbGciOiJIUzI1Ni...
```

---

# 3. General Routes

| Method | Route              | Authentication | Request | Response                            |
| ------ | ------------------ | -------------- | ------- | ----------------------------------- |
| `GET`  | `/`                | No             | None    | Welcome message                     |
| `GET`  | `/health`          | No             | None    | Health status                       |
| `GET`  | `/openwebui/`      | No             | None    | Open WebUI health response          |
| `GET`  | `/openwebui/db`    | No             | None    | Open WebUI database health response |
| `GET`  | `/openwebui/ready` | No             | None    | Open WebUI readiness response       |
| `GET`  | `/openwebui/models` | No             | None    | Open WebUI available models list       |

### `GET /`

Response:

```json
{
  "message": "Welcome to Internal chat ai platform based on open web ui"
}
```

### `GET /health`

Response:

```json
{
  "status": "ok"
}
```

### `GET /openwebui`

Response:

```json
{
  "status": true
}
```

### `GET /openwebui/db`

Response:

```json
{
  "status": true
}
```

### `GET /openwebui/ready`

Response:

```json
{
  "status": true
}
```

### `GET /openwebui/models`

Response:

```json
[
  {
    "id": "gemini-3.1-flash-lite",
    "name": "gemini-3.1-flash-lite",
    "owned_by": "openai",
    "openai": {
      "id": "gemini-3.1-flash-lite",
      "name": "gemini-3.1-flash-lite",
      "owned_by": "openai",
      "openai": {
        "id": "gemini-3.1-flash-lite"
      },
      "urlIdx": 1,
      "connection_type": "external"
    },
    "urlIdx": 1,
    "connection_type": "external",
    "provider": "",
    "actions": [],
    "filters": [],
    "tags": []
  }
]
```

---

# 4. Authentication Routes

## Auth Route Table

| Method | Route         | Authentication | Request                           | Response        |
| ------ | ------------- | -------------- | --------------------------------- | --------------- |
| `POST` | `/auth/login` | No             | Form data: `username`, `password` | `TokenResponse` |
| `GET`  | `/auth/me`    | Yes            | Bearer token                      | `UserResponse`  |

---

## `POST /auth/login`

Login uses **form data**, not JSON.

### Request

```text
username=example
password=example123
```

Content type:

```text
application/x-www-form-urlencoded
```

### Success Response

```json
{
  "access_token": "JWT_TOKEN_HERE",
  "token_type": "bearer"
}
```

### Error

Invalid username/password:

```json
{
  "detail": "Incorrect username or password"
}
```

Status:

```text
401 Unauthorized
```

---

## `GET /auth/me`

Returns the currently authenticated user.

### Headers

```http
Authorization: Bearer <access_token>
```

### Response

```json
{
  "id": "UUID",
  "name": "Fatimah",
  "username": "fatimah"
}
```

---

# 5. Chat Routes

## Chat Route Table

| Method   | Route                       | Authentication | Request                                     | Response              |
| -------- | --------------------------- | -------------- | ------------------------------------------- | --------------------- |
| `GET`    | `/chats/`                   | Yes            | None                                        | `list[ChatResponse]`  |
| `POST`   | `/chats/`                   | Yes            | `MessageCreate` + optional query parameters | `ChatMessageResponse` |
| `GET`    | `/chats/{chat_id}`          | Yes            | `chat_id`                                   | `ChatDetailResponse`  |
| `PUT`    | `/chats/{chat_id}`          | Yes            | `title` query parameter                     | `ChatResponse`        |
| `DELETE` | `/chats/{chat_id}`          | Yes            | `chat_id`                                   | Success message       |
| `POST`   | `/chats/{chat_id}/messages` | Yes            | `MessageCreate` + optional query parameters | `MessageResponse`     |

---

## `GET /chats/`

Returns the authenticated user's chats.

### Response

```json
[
  {
    "id": "UUID",
    "title": "How does our vacation policy work?",
    "created_date": "2026-09-17T10:30:00",
    "update_date": "2026-09-17T10:35:00",
    "user_id": "UUID"
  }
]
```

The frontend can use this for the **recent chats sidebar**.

---

## `POST /chats/`

Creates a new chat and sends the first message.

### Request Body

```json
{
  "message": {
    "role": "string",
    "content": "string"
  },
  "file_ids": [
    "string"
  ],
  "knowledge_ids": [
    "string"
  ]
}
```

### Optional Query Parameters/Body

| Parameter       | Type   | Required | Description                                |
| --------------- | ------ | -------- | ------------------------------------------ |
| `file_ids`      | UUID   | No       | Documents to use for the chat              |
| `knowledge_ids` | UUID   | No       | Knowledge bases to use                     |
| `model`         | string | Yes       | AI model. get a valid model name from the /openwebui/models. Reliable models list [Reliable models list](#reliable--free-gemini-models) |


### Response

```json
{
  "chat": {
    "id": "UUID",
    "title": "What is our vacation policy?",
    "created_date": "2026-09-17T10:30:00",
    "update_date": "2026-09-17T10:30:00",
    "user_id": "UUID"
  },
  "usermessage": {
    "id": "UUID",
    "role": "user",
    "content": "What is our vacation policy?",
    "created_date": "2026-09-17T10:30:00"
  },
  "assistantmessage": {
    "id": "UUID",
    "role": "assistant",
    "content": "According to the company policy...",
    "created_date": "2026-09-17T10:30:02"
  }
}
```

The frontend can use this response to immediately display:

```text
User message
      ↓
AI response
```

---

## `GET /chats/{chat_id}`

Returns one chat, including its messages and documents.

### Response

```json
{
  "id": "UUID",
  "title": "Vacation Policy",
  "created_date": "2026-09-17T10:30:00",
  "update_date": "2026-09-17T10:35:00",
  "user_id": "UUID",
  "messages": [
    {
      "id": "UUID",
      "role": "user",
      "content": "What is our vacation policy?",
      "created_date": "2026-09-17T10:30:00"
    },
    {
      "id": "UUID",
      "role": "assistant",
      "content": "According to the company policy...",
      "created_date": "2026-09-17T10:30:02"
    }
  ],
  "documents": [
    {
      "id": "UUID",
      "name": "company_policy.pdf",
      "created_date": "2026-09-17T10:20:00"
    }
  ]
}
```

This can be used when opening a chat from the sidebar/history.

---

## `PUT /chats/{chat_id}`

Updates a chat title.

### Current Request Format

The title is currently a **query parameter**, not a JSON body.

```text
PUT /chats/{chat_id}?title=New%20Chat%20Title
```

### Response

```json
{
  "id": "UUID",
  "title": "New Chat Title",
  "created_date": "2026-09-17T10:30:00",
  "update_date": "2026-09-17T11:00:00",
  "user_id": "UUID"
}
```

---

## `POST /chats/{chat_id}/messages`

Sends a new message to an existing chat.

### Request Body

```json
{
  "message": {
    "role": "string",
    "content": "string"
  },
  "file_ids": [
    "string"
  ],
  "knowledge_ids": [
    "string"
  ]
}
```

### Optional Body

```text
file_ids
knowledge_ids
```

### Response

```json
{
  "id": "UUID",
  "role": "assistant",
  "content": "Sure. The policy means...",
  "created_date": "2026-09-17T11:05:00"
}
```

---

## `DELETE /chats/{chat_id}`

Deletes a chat belonging to the authenticated user.

### Response

```json
{
  "message": "Chat deleted successfully"
}
```

---

# 6. Document Routes

The current MVP supports:

* PDF
* TXT

## Document Route Table

| Method   | Route                              | Authentication | Request        | Response                   |
| -------- | ---------------------------------- | -------------- | -------------- | -------------------------- |
| `POST`   | `/documents/`                      | Yes            | Multipart file | `DocumentResponse`         |
| `GET`    | `/documents/`                      | Yes            | None           | `list[DocumentResponse]`   |
| `GET`    | `/documents/{document_id}`         | Yes            | `document_id`  | `DocumentResponse`         |
| `GET`    | `/documents/{document_id}/content` | Yes            | `document_id`  | Raw file content           |
| `DELETE` | `/documents/{document_id}`         | Yes            | `document_id`  | Open WebUI delete response |

---

## `POST /documents/`

Uploads a document.

### Request

This endpoint uses:

```text
multipart/form-data
```

The file field must be named:

```text
file
```

Example:

```text
file = company_policy.pdf
```

### Supported Files

```text
application/pdf
text/plain
```

### Response

```json
{
  "id": "UUID",
  "name": "company_policy.pdf",
  "created_date": "2026-09-17T10:20:00"
}
```

The frontend only needs the application's document ID for future requests.

---

## `GET /documents/`

Returns documents available to the current user.

This includes:

* Documents owned by the current user
* Company/shared documents

### Response

```json
[
  {
    "id": "UUID",
    "name": "company_policy.pdf",
    "created_date": "2026-09-17T10:20:00"
  },
  {
    "id": "UUID",
    "name": "employee_handbook.pdf",
    "created_date": "2026-09-16T09:00:00"
  }
]
```

---

## `GET /documents/{document_id}`

Returns one document.

### Response

```json
{
  "id": "UUID",
  "name": "company_policy.pdf",
  "created_date": "2026-09-17T10:20:00"
}
```

---

## `GET /documents/{document_id}/content`

Returns the actual document content.

This endpoint does **not** return JSON.

For example:

```text
Content-Type: application/pdf
```

or:

```text
Content-Type: text/plain
```

The frontend can use the response according to its returned `Content-Type`.

---

## `DELETE /documents/{document_id}`

Deletes a user-owned document.

### Response

```json
{
  "message": "File deleted successfully"
}
```

---

# 7. Knowledge Base Routes

## Knowledge Route Table

| Method   | Route                                               | Authentication | Request                   | Response                      |
| -------- | --------------------------------------------------- | -------------- | ------------------------- | ----------------------------- |
| `GET`    | `/knowledge/`                                       | Yes            | None                      | `list[KnowledgeBaseResponse]` |
| `POST`   | `/knowledge/`                                       | Yes            | `KnowledgeBaseCreate`     | `KnowledgeBaseResponse`       |
| `PUT`    | `/knowledge/{knowledge_id}`                         | Yes            | `KnowledgeBaseCreate`     | `KnowledgeBaseResponse`       |
| `GET`    | `/knowledge/{knowledge_id}`                         | Yes            | `knowledge_id`            | `KnowledgeBaseDetailResponse` |
| `POST`   | `/knowledge/{knowledge_id}/documents`               | Yes            | `file_id` query parameter | `DocumentResponse`            |
| `POST`   | `/knowledge/{knowledge_id}/documents/{document_id}` | Yes            | Path parameters           | Success message               |
| `DELETE` | `/knowledge/{knowledge_id}`                         | Yes            | `knowledge_id`            | Success message               |

---

## `GET /knowledge/`

Returns knowledge bases available to the current user.

This includes:

* User-owned knowledge bases
* Company/shared knowledge bases

### Response

```json
[
  {
    "id": "UUID",
    "title": "Company Policies",
    "description": "Company policies and procedures",
    "created_date": "2026-09-17T09:00:00",
    "updated_date": "2026-09-17T10:00:00"
  }
]
```

---

## `POST /knowledge/`

Creates a new knowledge base.

### Request Body

```json
{
  "title": "Company Policies",
  "description": "Company policies and procedures"
}
```

### Response

```json
{
  "id": "UUID",
  "title": "Company Policies",
  "description": "Company policies and procedures",
  "created_date": "2026-09-17T09:00:00",
  "updated_date": "2026-09-17T09:00:00"
}
```

---

## `PUT /knowledge/{knowledge_id}`

Updates an existing knowledge base.

### Request Body

```json
{
  "title": "Updated Company Policies",
  "description": "Updated description"
}
```

### Response

```json
{
  "id": "UUID",
  "title": "Updated Company Policies",
  "description": "Updated description",
  "created_date": "2026-09-17T09:00:00",
  "updated_date": "2026-09-17T11:00:00"
}
```

---

## `GET /knowledge/{knowledge_id}`

Returns a knowledge base and its documents.

### Response

```json
{
  "id": "UUID",
  "title": "Company Policies",
  "description": "Company policies and procedures",
  "created_date": "2026-09-17T09:00:00",
  "updated_date": "2026-09-17T10:00:00",
  "documents": [
    {
      "id": "UUID",
      "name": "vacation_policy.pdf",
      "created_date": "2026-09-17T09:30:00"
    },
    {
      "id": "UUID",
      "name": "employee_handbook.pdf",
      "created_date": "2026-09-17T09:35:00"
    }
  ]
}
```

This can be used for the **Knowledge page** where the frontend displays the documents belonging to a knowledge base.

---

## `POST /knowledge/{knowledge_id}/documents`

Adds an existing document to a knowledge base.

### Request

The document ID is currently a query parameter:

```text
POST /knowledge/{knowledge_id}/documents?file_id=DOCUMENT_UUID
```

### Response

```json
{
  "id": "UUID",
  "name": "vacation_policy.pdf",
  "created_date": "2026-09-17T09:30:00"
}
```

---

## `POST /knowledge/{knowledge_id}/documents/{document_id}`

Removes a document from a knowledge base.

### Request

```text
POST /knowledge/KNOWLEDGE_UUID/documents/DOCUMENT_UUID
```

### Response

```json
{
  "message": "Document removed from knowledge base successfully"
}
```

> Note: this is currently implemented as `POST`. If the route is changed to `DELETE` later, the frontend route should be updated accordingly.

---

## `DELETE /knowledge/{knowledge_id}`

Deletes a knowledge base belonging to the authenticated user.

### Response

```json
{
  "message": "Knowledge base deleted successfully"
}
```

---

# 8. Data Models

## User

```json
{
  "id": "UUID",
  "name": "Fatimah",
  "username": "fatimah"
}
```

---

## Chat

```json
{
  "id": "UUID",
  "title": "Company vacation policy",
  "created_date": "2026-09-17T10:30:00",
  "update_date": "2026-09-17T10:35:00",
  "user_id": "UUID"
}
```

---

## Message

```json
{
  "id": "UUID",
  "role": "user",
  "content": "What is our vacation policy?",
  "created_date": "2026-09-17T10:30:00"
}
```

Possible roles:

```text
user
assistant
```

---

## Document

```json
{
  "id": "UUID",
  "name": "company_policy.pdf",
  "created_date": "2026-09-17T10:20:00"
}
```

---

## Knowledge Base

```json
{
  "id": "UUID",
  "title": "Company Policies",
  "description": "Company policies and procedures",
  "created_date": "2026-09-17T09:00:00",
  "updated_date": "2026-09-17T10:00:00"
}
```

---

# 9. Common Frontend Flow

## Login

```text
POST /auth/login
        ↓
Receive JWT
        ↓
Store access token
        ↓
Send token with protected requests
```

---

## Open existing chat

```text
GET /chats/
        ↓
Display recent chats
        ↓
User selects chat
        ↓
GET /chats/{chat_id}
        ↓
Display messages
```

---

## Send message

For an existing chat:

```text
POST /chats/{chat_id}/messages
        ↓
Receive assistant message
        ↓
Display assistant response
```

For a new chat:

```text
POST /chats/
        ↓
Chat + user message + assistant message
        ↓
Display all three
```

---

## Upload document

```text
POST /documents/
        ↓
Receive DocumentResponse
        ↓
Store/use returned document UUID
```

---

## Create knowledge base

```text
POST /knowledge/
        ↓
Receive KnowledgeBaseResponse
        ↓
Display knowledge base
```

Then add documents:

```text
POST /knowledge/{knowledge_id}/documents?file_id={document_id}
```

---

# 10. Environment Variables

copy the `.env.example`

```env
POSTGRES_PASSWORD=your_postgres_password
DB_URL=localhost:543

JWT_SECRET_KEY=your_jwt_secret_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

GEMINI_API_KEY=your_gemini_api_key

OPEN_WEB_UI_API_URL=http://localhost:3000
OPENWEBUI_ADMIN_EMAIL=admin@example.com
OPENWEBUI_ADMIN_PASSWORD=your_password
```

## Where to obtain each value

| Variable                      | Purpose                            | Obtain from                                               |
| ----------------------------- | ---------------------------------- | --------------------------------------------------------- |
| `POSTGRES_PASSWORD`           | PostgreSQL database password       | `Your Postgres password that you use to connect to postgres in psql`      |
| `POSTGRES_HOST`           | PostgreSQL database host       | `localhost:5432 or the azure postgres host`      |
| `POSTGRES_USER`           | PostgreSQL database user       | `openwebuiadmin`      |
| `POSTGRES_DB`           | PostgreSQL database host       | openwebui      |
| `JWT_SECRET_KEY`              | Secret used to sign JWT tokens     | `https://jwtsecretkeygenerator.com/` |
| `JWT_ALGORITHM`               | JWT signing algorithm              | `HS256`                                                   |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime                     | `1440`                                     |
| `GEMINI_API_KEY`              | Gemini API key                     | `https://aistudio.google.com/api-keys`                      |
|`OPEN_WEB_UI_API_URL`          | Address of the Open WebUI instance | `http://localhost:3000`       
| `OPENWEBUI_ADMIN_EMAIL`         | Open web ui admin email | `Whatever email you want`       |
| `OPENWEBUI_ADMIN_PASSWORD`         | open web ui admin passwordinstance | `Whatever password you want`  |

---

# 11. Frontend Authentication Reminder

Every protected request needs:

```http
Authorization: Bearer <access_token>
```

Protected routes include:

```text
GET    /auth/me

GET    /chats/
POST   /chats/
GET    /chats/{chat_id}
PUT    /chats/{chat_id}
DELETE /chats/{chat_id}
POST   /chats/{chat_id}/messages

GET    /documents/
POST   /documents/
GET    /documents/{document_id}
GET    /documents/{document_id}/content
DELETE /documents/{document_id}

GET    /knowledge/
POST   /knowledge/
PUT    /knowledge/{knowledge_id}
GET    /knowledge/{knowledge_id}
POST   /knowledge/{knowledge_id}/documents
POST   /knowledge/{knowledge_id}/documents/{document_id}
DELETE /knowledge/{knowledge_id}
```

---

# 12. Important Current Backend Notes

These are implementation details the frontend should be aware of.

### Chat title update

The current endpoint uses a query parameter:

```text
PUT /chats/{chat_id}?title=New%20Title
```

It does not currently accept:

```json
{
  "title": "New Title"
}
```

### Document upload

Document upload is `multipart/form-data`, not JSON.

The field name is:

```text
file
```

### Chat message options

`file_ids`, `knowledge_ids`, and `model` are currently query parameters rather than JSON fields.

### Document content

`GET /documents/{document_id}/content` returns the actual file, not a JSON object.

### Shared resources

Documents and knowledge bases with `user_id = null` represent company/shared resources.

The list and detail endpoints allow users to see these shared resources.

### Open WebUI

The frontend should not communicate directly with Open WebUI.

All Open WebUI communication goes through FastAPI.

### Reliable & Free Gemini Models

The following Gemini models have consistently returned responses during testing while remaining available on the free tier:

* `gemini-3.1-flash-lite`
* `gemini-3.5-flash-lite`
* `gemini-3.5-flash`

> **Note:** Model IDs may change over time. To get the currently available model IDs, use the `/openwebui/models` route and pass the exact ID returned by the endpoint to the chat endpoint.


---

# 13. API Documentation

FastAPI automatically provides interactive API documentation.

During development, the frontend can use the Swagger UI to test requests and inspect the actual schemas.

```text
/docs
```

The frontend developer can use Swagger to verify:

* request parameters
* request bodies
* authentication
* response schemas
* status codes

---

# 14. MVP Endpoint Summary

### Authentication

```text
POST /auth/login
GET  /auth/me
```

### Chats

```text
GET    /chats/
POST   /chats/
GET    /chats/{chat_id}
PUT    /chats/{chat_id}
DELETE /chats/{chat_id}
POST   /chats/{chat_id}/messages
```

### Documents

```text
GET    /documents/
POST   /documents/
GET    /documents/{document_id}
GET    /documents/{document_id}/content
DELETE /documents/{document_id}
```

### Knowledge

```text
GET    /knowledge/
POST   /knowledge/
PUT    /knowledge/{knowledge_id}
GET    /knowledge/{knowledge_id}
POST   /knowledge/{knowledge_id}/documents
POST   /knowledge/{knowledge_id}/documents/{document_id}
DELETE /knowledge/{knowledge_id}
```

### Health

```text
GET /health

GET /openwebui/
GET /openwebui/db
GET /openwebui/ready
```
