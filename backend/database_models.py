from sqlalchemy import  ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from database import Base
from datetime import date


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
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
    
class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] 
    created_date: Mapped[date] 
    update_date: Mapped[date] 
    user_id: Mapped[int] = mapped_column(
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

    id: Mapped[int] = mapped_column(primary_key=True)
    role: Mapped[str]
    content: Mapped[str]
    created_date: Mapped[date]
    chat_id: Mapped[int] = mapped_column(
        ForeignKey("chats.id")
    )
    chat: Mapped["Chat"] = relationship(
        "Chat",
        back_populates="messages"
    )

class Document(Base):
    __tablename__ = "documents"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    created_date: Mapped[date]
    chat_id: Mapped[int] = mapped_column(
        ForeignKey("chats.id"),
        nullable=True
    )
    chat: Mapped["Chat"] = relationship(
        "Chat",
        back_populates="documents"
    )  
    knowledge_id: Mapped[int] = mapped_column(
        ForeignKey("knowledges.id"),
        nullable=True
    )
    knowledge_base: Mapped["KnowledgeBase"] = relationship(
        "KnowledgeBase",
        back_populates="documents"
    )

class KnowledgeBase(Base):
    __tablename__ = "knowledges"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    description: Mapped[str]
    created_date: Mapped[date]
    updated_date: Mapped[date]
    documents: Mapped[List["Document"]] = relationship(
            "Document", 
            back_populates="knowledge_base"
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )
    user: Mapped["User"] = relationship(
        "User",
        back_populates="knowledge_bases"
    )

    