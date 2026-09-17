from sqlalchemy import  ForeignKey, CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from database import Base
from datetime import datetime
from uuid import uuid4, UUID

class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] 
    username: Mapped[str] 
    password: Mapped[str]  
    chats: Mapped[List["Chat"]] = relationship(
        "Chat", 
        back_populates="user", 
        cascade="all, delete-orphan"
    )
    knowledge_bases: Mapped[List["KnowledgeBase"]] = relationship(
        "KnowledgeBase", 
        back_populates="user", 
        cascade="all, delete-orphan"
    )
    documents: Mapped[List["Document"]] = relationship(
        "Document", 
        back_populates="user", 
        cascade="all, delete-orphan"
    )
    
class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str] 
    created_date: Mapped[datetime] 
    update_date: Mapped[datetime] 
    user_id: Mapped[UUID] = mapped_column(
            ForeignKey("users.id")
        )
    user: Mapped["User"] = relationship(
        "User",
        back_populates="chats"
    )
    messages: Mapped[List["Message"]] = relationship(
        "Message", 
        back_populates="chat", 
        cascade="all, delete-orphan"
    )
    documents: Mapped[List["Document"]] = relationship(
        "Document", 
        back_populates="chat"
    )
    
class Message(Base):
    __tablename__ = "messages"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    role: Mapped[str] = mapped_column(String(10), CheckConstraint("role IN ('user', 'assistant')", name="message_role_check"))
    content: Mapped[str]
    created_date: Mapped[datetime]
    model_name: Mapped[str | None]
    chat_id: Mapped[UUID] = mapped_column(
        ForeignKey("chats.id")
    )
    chat: Mapped["Chat"] = relationship(
        "Chat",
        back_populates="messages"
    )

class Document(Base):
    __tablename__ = "documents"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str]
    created_date: Mapped[datetime]
    open_web_ui_file_id: Mapped[str]
    chat_id: Mapped[UUID] = mapped_column(
        ForeignKey("chats.id"),
        nullable=True
    )
    chat: Mapped["Chat"] = relationship(
        "Chat",
        back_populates="documents"
    )  
    knowledge_id: Mapped[UUID] = mapped_column(
        ForeignKey("knowledges.id"),
        nullable=True
    )
    knowledge_base: Mapped["KnowledgeBase"] = relationship(
        "KnowledgeBase",
        back_populates="documents"
    )
    user_id: Mapped[UUID] = mapped_column(
            ForeignKey("users.id")
        )
    user: Mapped["User"] = relationship(
        "User",
        back_populates="documents"
    )

class KnowledgeBase(Base):
    __tablename__ = "knowledges"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str]
    description: Mapped[str]
    created_date: Mapped[datetime]
    updated_date: Mapped[datetime]
    open_web_ui_knowledge_id: Mapped[str]
    documents: Mapped[List["Document"]] = relationship(
            "Document", 
            back_populates="knowledge_base"
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id")
    )
    user: Mapped["User"] = relationship(
        "User",
        back_populates="knowledge_bases"
    )