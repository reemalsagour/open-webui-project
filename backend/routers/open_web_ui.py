from fastapi import APIRouter
from open_web_ui_api import healthy, ready, db_healthy, get_available_models

router = APIRouter(
    prefix="/openwebui",
    tags=["Open Web UI"],
)

@router.get("/")
def open_web_ui_health_check():
    return healthy()
    
@router.get("/db")
def open_web_ui_db_health_check():
    return db_healthy()
    
@router.get("/ready")
def open_web_ui_ready_check():
    return ready()

@router.get("/models")
def open_web_ui_available_models():
    return get_available_models()