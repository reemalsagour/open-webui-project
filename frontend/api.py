import requests
import os

# =========================================================
# API CONFIGURATION
# =========================================================

BASE_URL = os.getenv(
    "BACKEND_URL",
    "http://localhost:8000"
)

# =========================================================
# HELPER FUNCTIONS
# =========================================================

def auth_headers(token):
    """
    Create the Authorization header required
    by protected FastAPI routes.
    """
    return {
        "Authorization": f"Bearer {token}"
    }


# =========================================================
# AUTHENTICATION
# =========================================================

def login(username, password):
    """
    Log the user in and return the FastAPI response.
    """

    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={
            "username": username,
            "password": password
        },
        timeout=10
    )

    return response


def get_current_user(token):
    """
    Return the currently authenticated user.
    """

    response = requests.get(
        f"{BASE_URL}/auth/me",
        headers=auth_headers(token),
        timeout=10
    )

    return response


# =========================================================
# MODELS
# =========================================================

def get_models(token):
    """
    Get the currently available AI models from Open WebUI
    through the FastAPI backend.

    The frontend must not communicate directly with
    Open WebUI.
    """

    response = requests.get(
        f"{BASE_URL}/openwebui/models",
        headers=auth_headers(token),
        timeout=15
    )

    return response


# =========================================================
# CHATS
# =========================================================

def get_chats(token):
    """
    Get all chats belonging to the current user.
    """

    response = requests.get(
        f"{BASE_URL}/chats/",
        headers=auth_headers(token),
        timeout=10
    )

    return response


def get_chat(token, chat_id):
    """
    Get one chat including its messages
    and associated documents.
    """

    response = requests.get(
        f"{BASE_URL}/chats/{chat_id}",
        headers=auth_headers(token),
        timeout=10
    )

    return response


def create_chat(
    token,
    message,
    model,
    file_ids=None,
    knowledge_ids=None
):
    """
    Create a new chat and send the first user message.
    """

    params = {
        "model": model
    }

    body = {
        "message": {
            "role": "user",
            "content": message
        }
    }
    
    if file_ids:
        body["file_ids"] = file_ids

    if knowledge_ids:
        body["knowledge_ids"] = knowledge_ids

    response = requests.post(
        f"{BASE_URL}/chats/",
        headers=auth_headers(token),
        params=params,
        json=body,
        timeout=60
    )

    return response


def send_message(
    token,
    chat_id,
    message,
    model,
    file_ids=None,
    knowledge_ids=None
):
    """
    Send a message to an existing chat.
    """

    params = {
        "model": model
    }

    body = {
           "message": {
               "role": "user",
               "content": message
           }
       }
       
    if file_ids:
        body["file_ids"] = file_ids

    if knowledge_ids:
        body["knowledge_ids"] = knowledge_ids

    response = requests.post(
        f"{BASE_URL}/chats/{chat_id}/messages",
        headers=auth_headers(token),
        params=params,
        json=body,
        timeout=60
    )

    return response


def update_chat_title(token, chat_id, title):
    """
    Update the title of an existing chat.

    The backend currently expects the title
    as a query parameter.
    """

    response = requests.put(
        f"{BASE_URL}/chats/{chat_id}",
        headers=auth_headers(token),
        params={
            "title": title
        },
        timeout=10
    )

    return response


def delete_chat(token, chat_id):
    """
    Delete an existing chat.
    """

    response = requests.delete(
        f"{BASE_URL}/chats/{chat_id}",
        headers=auth_headers(token),
        timeout=10
    )

    return response


# =========================================================
# DOCUMENTS
# =========================================================

def get_documents(token):
    """
    Get documents available to the current user.
    """

    response = requests.get(
        f"{BASE_URL}/documents/",
        headers=auth_headers(token),
        timeout=10
    )

    return response


def get_document(token, document_id):
    """
    Get information about one document.
    """

    response = requests.get(
        f"{BASE_URL}/documents/{document_id}",
        headers=auth_headers(token),
        timeout=10
    )

    return response


def upload_document(token, uploaded_file):
    """
    Upload a PDF or TXT document.

    FastAPI expects multipart/form-data
    with the field name 'file'.
    """

    files = {
        "file": (
            uploaded_file.name,
            uploaded_file.getvalue(),
            uploaded_file.type
        )
    }

    response = requests.post(
        f"{BASE_URL}/documents/",
        headers=auth_headers(token),
        files=files,
        timeout=60
    )

    return response


def get_document_content(token, document_id):
    """
    Get the actual document content.
    """

    response = requests.get(
        f"{BASE_URL}/documents/{document_id}/content",
        headers=auth_headers(token),
        timeout=30
    )

    return response


def delete_document(token, document_id):
    """
    Delete a user-owned document.
    """

    response = requests.delete(
        f"{BASE_URL}/documents/{document_id}",
        headers=auth_headers(token),
        timeout=20
    )

    return response


# =========================================================
# KNOWLEDGE BASES
# =========================================================

def get_knowledge_bases(token):
    """
    Get knowledge bases available to the current user.
    """

    response = requests.get(
        f"{BASE_URL}/knowledge/",
        headers=auth_headers(token),
        timeout=10
    )

    return response


def get_knowledge_base(token, knowledge_id):
    """
    Get one knowledge base including its documents.
    """

    response = requests.get(
        f"{BASE_URL}/knowledge/{knowledge_id}",
        headers=auth_headers(token),
        timeout=10
    )

    return response


def create_knowledge_base(token, title, description):
    """
    Create a new knowledge base.
    """

    response = requests.post(
        f"{BASE_URL}/knowledge/",
        headers=auth_headers(token),
        json={
            "title": title,
            "description": description
        },
        timeout=15
    )

    return response


def update_knowledge_base(
    token,
    knowledge_id,
    title,
    description
):
    """
    Update the title and description
    of an existing knowledge base.
    """

    response = requests.put(
        f"{BASE_URL}/knowledge/{knowledge_id}",
        headers=auth_headers(token),
        json={
            "title": title,
            "description": description
        },
        timeout=15
    )

    return response


def add_document_to_knowledge(
    token,
    knowledge_id,
    document_id
):
    """
    Add an existing document to a knowledge base.

    The backend currently expects file_id
    as a query parameter.
    """

    response = requests.post(
        f"{BASE_URL}/knowledge/{knowledge_id}/documents",
        headers=auth_headers(token),
        params={
            "file_id": document_id
        },
        timeout=20
    )

    return response


def remove_document_from_knowledge(
    token,
    knowledge_id,
    document_id
):
    """
    Remove a document from a knowledge base.

    NOTE:
    The current backend uses POST for this route.
    """

    response = requests.post(
        (
            f"{BASE_URL}/knowledge/"
            f"{knowledge_id}/documents/{document_id}"
        ),
        headers=auth_headers(token),
        timeout=20
    )

    return response


def delete_knowledge_base(token, knowledge_id):
    """
    Delete a knowledge base.
    """

    response = requests.delete(
        f"{BASE_URL}/knowledge/{knowledge_id}",
        headers=auth_headers(token),
        timeout=20
    )

    return response


# =========================================================
# SYSTEM HEALTH
# =========================================================

def check_health():
    """
    Check whether the FastAPI backend is running.
    """

    response = requests.get(
        f"{BASE_URL}/health",
        timeout=10
    )

    return response