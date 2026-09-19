from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from pydantic_models import DocumentResponse
from database import get_db
from sqlalchemy import or_
from sqlalchemy.orm import Session
from database_models import Document, User, Chat, KnowledgeBase
from datetime import datetime
from open_web_ui_api import upload_file, wait_for_file_processing, get_file_content_by_id, delete_file_by_id
from auth_logic import get_current_user
from uuid import UUID
from fastapi.responses import Response

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)

@router.post("/", response_model=DocumentResponse)
async def upload_a_document(db: Session = Depends(get_db), 
                            file: UploadFile = File(...), 
                            current_user: User = Depends(get_current_user)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file was uploaded")
    
    allowed_content_types = ["application/pdf", "text/plain"]

    if file.content_type not in allowed_content_types:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and TXT files are supported."
        )
    
    response_data = upload_file(file)
    
    await wait_for_file_processing(file_id=response_data)
    
    document = Document(
            name=file.filename,
            created_date=datetime.now(),
            user_id = current_user.id,
            open_web_ui_file_id = response_data
        )
    
    db.add(document)
    db.commit()
    db.refresh(document)
    return document

@router.get("/", response_model=list[DocumentResponse])
def list_available_documents(db: Session = Depends(get_db),
                             current_user: User = Depends(get_current_user)):
    documents = db.query(Document).filter(or_(Document.user_id == current_user.id, Document.user_id == None)).all()
    return documents

@router.get("/{document_id}", response_model=DocumentResponse)
def get_document_by_id(document_id: UUID ,
                       db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    document = db.query(Document).filter(Document.id == document_id,or_(Document.user_id == current_user.id,Document.user_id.is_(None))).first()
    if document is None:
            raise HTTPException(status_code=404, detail="Document not found")
    return document

@router.get("/{document_id}/content")
def get_document_content_by_id(document_id: UUID ,
                       db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    document = db.query(Document).filter(Document.id == document_id,or_(Document.user_id == current_user.id,Document.user_id.is_(None))).first()
    if document is None:
            raise HTTPException(status_code=404, detail="Document not found")
        
    file = get_file_content_by_id(document.open_web_ui_file_id)
    return Response(
        content=file.content,
        media_type=file.headers.get("content-type")
    )       


@router.delete("/{document_id}")
def delete_document_content_by_id(document_id: UUID, 
                          db: Session = Depends(get_db),
                          current_user: User = Depends(get_current_user)):
    document = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id).first()
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    response_data = delete_file_by_id(document.open_web_ui_file_id)
    
    db.delete(document)
    db.commit()
    return response_data