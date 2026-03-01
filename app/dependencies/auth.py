from fastapi import Depends
from fastapi.security import HTTPBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.config import settings
from app.models.user import User
from app.exceptions.custom_exceptions import UnauthorizedException, ForbiddenException

security = HTTPBearer()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token=Depends(security), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("user_id")
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise UnauthorizedException("Invalid token")
        return user
    except JWTError:
        raise UnauthorizedException("Invalid token")

def admin_only(user: User = Depends(get_current_user)):
    if user.role != "admin":
        raise ForbiddenException("Admin access required")
    return user
