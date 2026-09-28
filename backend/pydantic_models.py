from datetime import datetime
from pydantic import BaseModel, ConfigDict
from uuid import UUID
from typing import Optional

# Auth
class UserResponse(BaseModel):
    id: UUID
    name: str
    username: str

    model_config = ConfigDict(from_attributes=True)
    
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    
# Chats
class ChatResponse(BaseModel):
    id: UUID
    title: str
    created_date: datetime
    update_date: datetime
    user_id: UUID

    model_config = ConfigDict(from_attributes=True)

# Messages
class MessageCreate(BaseModel):
    role: str
    content: str

class MessageResponse(BaseModel):
    id: UUID
    role: str
    content: str
    created_date: datetime

    model_config = ConfigDict(from_attributes=True)
    
class ChatMessageResponse(BaseModel):
    chat: ChatResponse
    usermessage: MessageResponse
    assistantmessage: MessageResponse

# Documents
class DocumentResponse(BaseModel):
    id: UUID
    name: str
    created_date: datetime
    user: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)

# Knowledge Bases
class KnowledgeBaseCreate(BaseModel):
    title: str
    description: str
    
    
class KnowledgeBaseResponse(BaseModel):
    id: UUID
    title: str
    description: str
    created_date: datetime
    updated_date: datetime
    user: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)

# mixed
class KnowledgeBaseDetailResponse(KnowledgeBaseResponse):
    documents: list[DocumentResponse] = []
    
class ChatDetailResponse(ChatResponse):
    messages: list[MessageResponse] = []
    documents: list[DocumentResponse] = []