from datetime import date
from pydantic import BaseModel, ConfigDict

# Auth
class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    username: str

    model_config = ConfigDict(from_attributes=True)
    
# Chats
class ChatResponse(BaseModel):
    id: int
    title: str
    created_date: date
    update_date: date
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class ChatDetailResponse(ChatResponse):
    messages: list[MessageResponse] = []
    documents: list[DocumentResponse] = []

# Messages
class MessageCreate(BaseModel):
    content: str

class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_date: date

    model_config = ConfigDict(from_attributes=True)
    
class ChatMessageResponse(BaseModel):
    chat: ChatResponse
    message: MessageResponse

# Documents
class DocumentResponse(BaseModel):
    id: int
    name: str
    created_date: date
    chat_id: int | None
    knowledge_id: int | None

    model_config = ConfigDict(from_attributes=True)

# Knowledge Bases
class KnowledgeBaseResponse(BaseModel):
    id: int
    title: str
    description: str
    created_date: date
    updated_date: date

    model_config = ConfigDict(from_attributes=True)


class KnowledgeBaseDetailResponse(KnowledgeBaseResponse):
    documents: list[DocumentResponse] = []