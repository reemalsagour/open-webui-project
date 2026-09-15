from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from pydantic_models import KnowledgeBaseResponse, KnowledgeBaseDetailResponse, DocumentResponse, KnowledgeBaseCreate
from database import get_db
from sqlalchemy.orm import Session
from database_models import KnowledgeBase, Document
from datetime import date

router = APIRouter(
    prefix="/knowledge",
    tags=["Knowledge"],
)

@router.get("/", response_model=list[KnowledgeBaseResponse])
def list_available_knowledge_bases(db: Session = Depends(get_db)):
    knowledgebases = db.query(KnowledgeBase).all()
    return knowledgebases

@router.post("/", response_model=KnowledgeBaseResponse)
def create_a_knowledge_bases(knowledgebase: KnowledgeBaseCreate, db: Session = Depends(get_db)):
    new_knowledgebase = KnowledgeBase(
        title = knowledgebase.title,
        description = knowledgebase.description,
        created_date = date.today(),
        updated_date = date.today(),
        user_id=1
    )
    db.add(new_knowledgebase)
    db.commit()
    db.refresh(new_knowledgebase)
    return new_knowledgebase

@router.get("/{knowledge_id}", response_model=KnowledgeBaseDetailResponse)
def get_knowledge_base_by_id(knowledge_id: int ,db: Session = Depends(get_db)):
    knowledgebase = db.query(KnowledgeBase).get(knowledge_id)
    if knowledgebase == None:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    return knowledgebase

@router.post("/{knowledge_id}/documents", response_model=DocumentResponse)
def upload_document_to_knowledge_base(knowledge_id: int,
                                      file: UploadFile = File(...),
                                      db: Session = Depends(get_db)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file was uploaded")
    
    document = Document(
                name=file.filename,
                created_date=date.today(),
                knowledge_id=knowledge_id
            )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document

@router.delete("/{knowledge_id}/documents/{document_id}")
def delete_document_from_knowledge_base(document_id: int, knowledge_id: int,db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id and Document.knowledge_id == knowledge_id).first()
    if document == None:
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(document)
    db.commit()
    return {"message": "Document deleted successfully"}

@router.delete("/{knowledge_id}")
def delete_document_from_knowledge_base(knowledge_id: int,db: Session = Depends(get_db)):
    knowledgebase = db.query(KnowledgeBase).filter(KnowledgeBase.id == knowledge_id and Document.knowledge_id == knowledge_id).first()
    if knowledgebase == None:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    db.delete(knowledgebase)
    db.commit()
    return {"message": "Knowledge base deleted successfully"}