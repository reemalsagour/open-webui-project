from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from database import get_db
from database_models import Chat, Message, User, Document, KnowledgeBase
from pydantic_models import ChatResponse, MessageCreate, MessageResponse, ChatMessageResponse, ChatDetailResponse
from datetime import datetime
from auth_logic import get_current_user
from uuid import UUID, uuid4
from open_web_ui_api import chat_with_model

router = APIRouter(
    prefix="/chats",
    tags=["Chats"],
)

# helper functions
def build_documents_and_knowledge(db: Session, current_user: User, file_ids: list[UUID] | None = None, knowledge_ids: list[UUID] | None = None):
    documents_and_knowledge_request_array = []
    
    if file_ids is not None:
            for file_id in file_ids:
                file = db.query(Document).filter(Document.id == file_id, or_(Document.user_id == current_user.id, Document.user_id == None)).first()
                if file is not None:
                    documents_and_knowledge_request_array.append({'type': 'file', 'id': file.open_web_ui_file_id})
                else:
                    raise HTTPException(status_code=404, detail="Document not found")
        
    if knowledge_ids is not None:
        for knowledge_id in knowledge_ids:
            knowledge_base = db.query(KnowledgeBase).filter(KnowledgeBase.id == knowledge_id, or_(KnowledgeBase.user_id == current_user.id, KnowledgeBase.user_id == None)).first()
            if knowledge_base is not None:
                documents_and_knowledge_request_array.append({'type': 'collection', 'id': knowledge_base.open_web_ui_knowledge_id})
            else:
                raise HTTPException(status_code=404, detail="Knowledge base not found")
    
    if len(documents_and_knowledge_request_array) > 0:
        return documents_and_knowledge_request_array
    else:
        return None
    

# routers
@router.get("/", response_model=list[ChatResponse])
def get_all_chats(current_user: User = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    chats = db.query(Chat).filter(Chat.user_id == current_user.id).all()
    return chats


@router.put("/{chat_id}", response_model=ChatResponse)
def update_chat_name(chat_id: UUID, 
                     title: str, 
                     current_user: User = Depends(get_current_user),
                     db: Session = Depends(get_db)):
    chat = db.query(Chat).filter(Chat.user_id == current_user.id, Chat.id == chat_id).first()
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    if title is None or len(title) == 0:
        raise HTTPException(status_code=422, detail="Please enter a valid title")
    chat.title = title
    db.add(chat)
    db.commit()
    return chat


@router.post("/", status_code=201, response_model=ChatMessageResponse)
def create_a_chat_and_send_message( model: str,
                                   message: MessageCreate, 
                                   file_ids: list[UUID] | None = None , 
                                   knowledge_ids: list[UUID] | None = None, 
                                   db: Session = Depends(get_db), 
                                   current_user: User = Depends(get_current_user)):
    title = message.content[:50]
    if len(message.content) > 50:
        title += "..."
        
    chat_id = uuid4()
        
    chat = Chat(
        id= chat_id,
        title=title,
        created_date=datetime.now(),
        update_date=datetime.now(),
        user_id=current_user.id
    )
    
    user_message = Message(
        role='user',
        content=message.content,
        created_date=datetime.now(),
        chat_id=chat.id,
    )
    
    try:
        db.add(chat)
        db.add(user_message)

        documents_and_knowledge_request_array = build_documents_and_knowledge(
            db,
            current_user,
            file_ids,
            knowledge_ids
        )
        
        if file_ids:
            documents = db.query(Document).filter(
                Document.id.in_(file_ids)
            ).all()

            chat.documents.extend(documents)

        response = chat_with_model(
            [{"role": "user", "content": message.content}],
            documents_and_knowledge_request_array,
            model
        )

        assistant_message = Message(
            role='assistant',
            content=response,
            model_name=model,
            created_date=datetime.now(),
            chat_id=chat_id
        )

        db.add(assistant_message)

        chat.update_date = datetime.now()

        db.commit()

        db.refresh(chat)
        db.refresh(user_message)
        db.refresh(assistant_message)

    except Exception:
        db.rollback()
        raise

    return {
        "chat": chat,
        "usermessage": user_message,
        "assistantmessage": assistant_message
    }
    

@router.get("/{chat_id}", response_model=ChatDetailResponse)
def get_chat_by_id(chat_id: UUID, 
                   db: Session = Depends(get_db), 
                   current_user: User = Depends(get_current_user)):
    chat = db.query(Chat).filter(Chat.user_id == current_user.id, Chat.id == chat_id).first()
    if chat is None:
         raise HTTPException(status_code=404, detail="Chat not found")
    return chat


@router.delete("/{chat_id}")
def delete_chat_by_id(chat_id: UUID, 
                      db: Session = Depends(get_db), 
                      current_user: User = Depends(get_current_user)):
    chat = db.query(Chat).filter(Chat.user_id == current_user.id, Chat.id == chat_id).first()
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    db.delete(chat)
    db.commit()
    return {"message": "Chat deleted successfully"}


@router.post("/{chat_id}/messages", response_model=MessageResponse)
def send_a_chat_message_to_an_existing_chat(chat_id: UUID,
                                            model: str,
                                            message: MessageCreate, 
                                            db: Session = Depends(get_db),
                                            file_ids: list[UUID] | None = None, 
                                            knowledge_ids: list[UUID] | None = None,
                                            current_user: User = Depends(get_current_user)):
    chat = db.query(Chat).filter(Chat.user_id == current_user.id, Chat.id == chat_id).first()
    if chat is None:
         raise HTTPException(status_code=404, detail="Chat not found")
        
    user_message = Message(
        role="user",
        content=message.content,
        created_date=datetime.now(),
        chat_id=chat_id
    )
    
    try:
        db.add(user_message)

        documents_and_knowledge_request_array = build_documents_and_knowledge(db,current_user,file_ids,knowledge_ids)
        
        if file_ids:
            documents = db.query(Document).filter(
                Document.id.in_(file_ids)
            ).all()

            existing_document_ids = {
                document.id for document in chat.documents
            }

            for document in documents:
                if document.id not in existing_document_ids:
                    chat.documents.append(document)
                    existing_document_ids.add(document.id)
                    
        message_history_array = []    
        for messages in chat.messages:
            message_history_array.append(
                {
                    "role": messages.role, 
                    "content": messages.content
                }
            )
        
        message_history_array.append(
            {
                "role": "user",
                "content": message.content
            }
        )
                
        response = chat_with_model(
            message_history_array, 
            documents_and_knowledge_request_array,
            model
        )

        assistant_message = Message (
            role='assistant',
            content=response,
            model_name=model,
            created_date=datetime.now(),
            chat_id=chat_id
        )

        db.add(assistant_message)

        chat.update_date = datetime.now()

        db.commit()

        db.refresh(chat)
        db.refresh(user_message)
        db.refresh(assistant_message)

    except Exception:
        db.rollback()
        raise
    
    return assistant_message