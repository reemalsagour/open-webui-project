from fastapi import APIRouter, Depends, Query, status, UploadFile

router = APIRouter(
    prefix="/knowledge",
    tags=["Knowledge"],
)

@router.get("/")
def list_available_knowledge_bases():
    return {
        "message": "list all knowledge bases"
    }

@router.get("/{knowledge_id}")
def get_knowledge_base_by_id():
    return {
        "message": "get a knowledge base"
    }

@router.post("/{knowledge_id}/documents")
def upload_document_to_knowledge_base(file: UploadFile = File(...)):
    return {
        "message": "add a document to knowledge base",
        "filename": file.filename,
        "content_type": file.content_type,
    }

@router.delete("/{knowledge_id}/documents/{document_id}")
def delete_document_from_knowledge_base():
    return {
        "message": "delete a document fromo knowledge base"
    }