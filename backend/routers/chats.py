from fastapi import APIRouter, Depends, Query, status
from pydantic_models import ChatResponse, ChatDetailResponse
from sqlalchemy.orm import Session
from database import get_db
from database_models import Chat, Message
from pydantic_models import ChatResponse, MessageCreate, MessageResponse, ChatMessageResponse
from datetime import date

router = APIRouter(
    prefix="/chats",
    tags=["Chats"],
)

@router.get("/", response_model=list[ChatResponse])
def get_all_chats(db: Session = Depends(get_db)):
    chats = db.query(Chat).all()
    return chats

@router.post("/", response_model=ChatMessageResponse)
def create_a_chat_and_send_message( message: MessageCreate, db: Session = Depends(get_db)):
    chat = Chat(
        title="temp title",
        created_date=date.today(),
        update_date=date.today(),
        user_id=1
    )
    db.add(chat)
    db.commit()
    db.refresh(chat)
    
    new_message = Message(
        role="user",
        content=message.content,
        created_date=date.today(),
        chat_id=chat.id
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    
    return {
        "chat": chat,
        "message": new_message
    }

@router.get("/{chat_id}", response_model=ChatDetailResponse)
def get_chat_by_id(chat_id: int, db: Session = Depends(get_db)):
    chat = db.query(Chat).get(chat_id)
    return chat

@router.delete("/{chat_id}")
def delete_chat_by_id(chat_id: int, db: Session = Depends(get_db)):
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    db.delete(chat)
    db.commit()
    return {"message": "Chat deleted successfully"}

@router.post("/{chat_id}/messages", response_model=MessageResponse)
def send_a_chat_message_to_an_existing_chat(chat_id: int, message: MessageCreate, db: Session = Depends(get_db)):
    new_message = Message(
            role="user",
            content=message.content,
            created_date=date.today(),
            chat_id=chat_id
        )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message