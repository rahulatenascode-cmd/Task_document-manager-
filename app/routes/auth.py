from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.services.user_service import register_user, login_user
from app.dependencies.auth import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    return register_user(data, db)

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    return login_user(data, db)