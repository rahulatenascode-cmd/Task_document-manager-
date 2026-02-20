from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token
from app.exceptions.custom_exceptions import BadRequestException, UnauthorizedException

def register_user(data, db: Session):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise BadRequestException("Email already registered")

    user = User(email=data.email, password=hash_password(data.password))
    db.add(user)
    db.commit()
    return {"message": "User registered successfully"}

def login_user(data, db: Session):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password):
        raise UnauthorizedException("Invalid credentials")

    return {
        "access_token": create_access_token({"user_id": user.id}),
        "refresh_token": create_refresh_token({"user_id": user.id})
    }