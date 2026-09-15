from fastapi import FastAPI
from database import engine, Base
from routers import chats, documents, knowledge, auth

app = FastAPI(
    title="Internal AI Chat Platform",
    description="An internal AI chat program based on open web ui",
    version="1.0.0",
)

Base.metadata.create_all(bind=engine)

app.include_router(chats.router)
app.include_router(documents.router)
app.include_router(knowledge.router)
app.include_router(auth.router)


@app.get("/")
def read_root():
    return {
        "message": "Welcome to Internal chat ai platform based on open web ui"
    }

@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }

@app.get("/health/openwebui")
def open_web_ui_health_check():
    return {
        "status": "ok"
    }