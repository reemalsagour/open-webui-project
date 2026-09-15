from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from pydantic_models import DocumentResponse
from database import get_db
from sqlalchemy.orm import Session
from database_models import Document
from datetime import date

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)

@router.post("/", response_model=DocumentResponse)
def upload_a_document(db: Session = Depends(get_db), 
                      file: UploadFile = File(...), 
                      chat_id: int | None = None, 
                      knowledge_id: int | None = None):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file was uploaded")
    
    document = Document(
            name=file.filename,
            created_date=date.today(),
            chat_id=chat_id,
            knowledge_id=knowledge_id
        )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document

@router.get("/", response_model=list[DocumentResponse])
def list_available_documents(db: Session = Depends(get_db)):
    documents = db.query(Document).all()
    return documents

@router.get("/{document_id}", response_model=DocumentResponse)
def get_document_by_id(document_id: int ,db: Session = Depends(get_db)):
    document = db.query(Document).get(document_id)
    if document == None:
            raise HTTPException(status_code=404, detail="Document not found")
    return document

@router.delete("/{document_id}")
def delete_document_by_id(document_id: int, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if document == None:
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(document)
    db.commit()
    return {"message": "Document deleted successfully"}