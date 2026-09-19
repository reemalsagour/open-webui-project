from fastapi import APIRouter, Depends, HTTPException
from pydantic_models import KnowledgeBaseResponse, KnowledgeBaseDetailResponse, DocumentResponse, KnowledgeBaseCreate
from database import get_db
from sqlalchemy import or_
from sqlalchemy.orm import Session
from database_models import KnowledgeBase, Document, User
from datetime import datetime
from auth_logic import get_current_user
from uuid import UUID
from open_web_ui_api import create_knowledge, update_knowledge_by_id, add_file_to_knowledge, remove_file_from_knowledge, delete_knowledge_by_id

router = APIRouter(
    prefix="/knowledge",
    tags=["Knowledge"],
)

@router.get("/", response_model=list[KnowledgeBaseResponse])
def list_available_knowledge_bases(db: Session = Depends(get_db),
                                   current_user: User = Depends(get_current_user)):
    knowledgebases = db.query(KnowledgeBase).filter(or_(KnowledgeBase.user_id == current_user.id, KnowledgeBase.user_id == None)).all()
    return knowledgebases

@router.post("/", response_model=KnowledgeBaseResponse)
def create_a_knowledge_bases(knowledgebase: KnowledgeBaseCreate, 
                             db: Session = Depends(get_db),
                             current_user: User = Depends(get_current_user)):
    new_knowledgebase = KnowledgeBase(
        title = knowledgebase.title,
        description = knowledgebase.description,
        created_date = datetime.now(),
        updated_date = datetime.now(),
        user_id=current_user.id
    )
    open_web_ui_knowledge_id = create_knowledge(knowledgebase.title, knowledgebase.description)
    new_knowledgebase.open_web_ui_knowledge_id = open_web_ui_knowledge_id
    db.add(new_knowledgebase)
    db.commit()
    db.refresh(new_knowledgebase)
    return new_knowledgebase

@router.put("/{knowledge_id}", response_model=KnowledgeBaseResponse)
def update_knowledge_base(knowledge_id: UUID, 
                          knowledgebase: KnowledgeBaseCreate,
                          current_user: User = Depends(get_current_user),
                          db: Session = Depends(get_db)):
    updated_knowledgebase = db.query(KnowledgeBase).filter(KnowledgeBase.user_id == current_user.id, KnowledgeBase.id == knowledge_id).first()
    if updated_knowledgebase is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    update_knowledge_by_id(updated_knowledgebase.open_web_ui_knowledge_id,knowledgebase.title,knowledgebase.description)
    
    updated_knowledgebase.title = knowledgebase.title
    updated_knowledgebase.description = knowledgebase.description
    updated_knowledgebase.updated_date = datetime.now()
    
    db.add(updated_knowledgebase)
    db.commit()
    return updated_knowledgebase

@router.get("/{knowledge_id}", response_model=KnowledgeBaseDetailResponse)
def get_knowledge_base_by_id(knowledge_id: UUID ,
                             db: Session = Depends(get_db),
                             current_user: User = Depends(get_current_user)):
    knowledgebase = db.query(KnowledgeBase).filter(KnowledgeBase.id == knowledge_id,or_(KnowledgeBase.user_id == current_user.id,KnowledgeBase.user_id.is_(None))).first()
    if knowledgebase == None:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    return knowledgebase

@router.post("/{knowledge_id}/documents", response_model=DocumentResponse)
def upload_document_to_knowledge_base(knowledge_id: UUID,
                                      file_id: UUID,
                                      db: Session = Depends(get_db),
                                      current_user: User = Depends(get_current_user)):
    knowledgebase = db.query(KnowledgeBase).filter(KnowledgeBase.id == knowledge_id, KnowledgeBase.user_id == current_user.id).first()
    if knowledgebase == None:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    
    document = db.query(Document).filter(Document.id == file_id,or_(Document.user_id == current_user.id,Document.user_id.is_(None))).first()
    if document == None:
        raise HTTPException(status_code=404, detail="Document not found")
    
    add_file_to_knowledge(knowledgebase.open_web_ui_knowledge_id, document.open_web_ui_file_id)
    
    knowledgebase.documents.append(document)
    knowledgebase.updated_date = datetime.now()
    db.add(knowledgebase)
    db.commit()
    db.refresh(knowledgebase)
    return document

@router.post("/{knowledge_id}/documents/{document_id}")
def remove_document_from_knowledge_base(document_id: UUID, 
                                        knowledge_id: UUID,
                                        db: Session = Depends(get_db),
                                        current_user: User = Depends(get_current_user)):
    knowledgebase = db.query(KnowledgeBase).filter(KnowledgeBase.id == knowledge_id, KnowledgeBase.user_id == current_user.id).first()
    if knowledgebase == None:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    
    document = db.query(Document).filter(Document.id == document_id).first()
    if document == None:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document not in knowledgebase.documents:
        raise HTTPException(
            status_code=404,
            detail="Document not found in knowledge base"
        )
    
    remove_file_from_knowledge(knowledgebase.open_web_ui_knowledge_id,document.open_web_ui_file_id)
    
    knowledgebase.documents.remove(document)
    
    db.add(document, knowledgebase)
    db.commit()
    return {"message": "Document removed from knowledge base successfully"}

@router.delete("/{knowledge_id}")
def delete_knowledge_base(knowledge_id: UUID,
                          db: Session = Depends(get_db),
                          current_user: User = Depends(get_current_user)):
    knowledgebase = db.query(KnowledgeBase).filter(KnowledgeBase.id == knowledge_id, KnowledgeBase.user_id == current_user.id).first()
    if knowledgebase == None:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    delete_knowledge_by_id(knowledgebase.open_web_ui_knowledge_id)
    db.delete(knowledgebase)
    db.commit()
    return {"message": "Knowledge base deleted successfully"}