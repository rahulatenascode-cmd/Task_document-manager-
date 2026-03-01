from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.services.user_service import register_user, login_user
from app.dependencies.auth import get_db
from app.dependencies.rate_limiter import (
    rate_limit_dependency,
    increment_attempt,
    reset_attempts,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    responses={
        429: {"description": "Rate limit exceeded - too many requests"}
    }
)
def register(
    data: RegisterRequest,
    request: Request,
    db: Session = Depends(get_db),
    _rl=Depends(rate_limit_dependency),
):
    """User registration with rate limiting on failures."""
    ip = request.client.host
    try:
        result = register_user(data, db)
    except Exception:
        increment_attempt(ip)
        raise
    else:
        reset_attempts(ip)
        return result


@router.post(
    "/login",
    response_model=TokenResponse,
    responses={
        429: {"description": "Rate limit exceeded - too many attempts"}
    }
)
def login(
    data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
    _rl=Depends(rate_limit_dependency),
):
    """Authenticate user with rate limiting on failed attempts."""
    ip = request.client.host
    try:
        tokens = login_user(data, db)
    except Exception:
        increment_attempt(ip)
        raise
    else:
        reset_attempts(ip)
        return tokens
