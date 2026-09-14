from fastapi import APIRouter, Depends, Query, status, File, UploadFile
from backend.pydantic_models import DocumentResponse

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)

@router.post("/", response_model=DocumentResponse)
def upload_a_document(file: UploadFile = File(...)):
    return {
        "message": "upload adocument",
        "filename": file.filename,
        "content_type": file.content_type,
    }

@router.get("/")
def list_available_documents():
    return {
        "message": "list available documents"
    }

@router.get("/{document_id}")
def get_document_by_id():
    return {
        "message": "get a documents"
    }

@router.delete("/{document_id}")
def delete_document_by_id():
    return {
        "message": "delete a documents"
    }