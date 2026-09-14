from fastapi import APIRouter, Depends, Query, status
from backend.pydantic_models import UserLogin, UserResponse

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)

@router.post("/login")
def login(user: UserLogin):
    return {
        "message": user
    }

@router.post("/logout")
def logout():
    return {
        "message": "auth logout"
    }

@router.get("/me", response_model=UserResponse)
def me():
    return {
        "message": "user"
    }