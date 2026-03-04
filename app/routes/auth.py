from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    VerifyEmailRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)
from app.services.user_service import (
    register_user,
    login_user,
    verify_email,
    forgot_password,
    reset_password,
)
from app.dependencies.auth import get_db, get_current_user
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


@router.post("/verify-email")
def verify_email_endpoint(
    data: VerifyEmailRequest,
    db: Session = Depends(get_db)
):
    """Verify user email with verification token"""
    return verify_email(data.token, db)


@router.post("/forgot-password")
def forgot_password_endpoint(
    data: ForgotPasswordRequest,
    request: Request,
    db: Session = Depends(get_db),
    _rl=Depends(rate_limit_dependency),
):
    """Request password reset link"""
    ip = request.client.host
    try:
        result = forgot_password(data.email, db)
    except Exception:
        increment_attempt(ip)
        raise
    else:
        reset_attempts(ip)
        return result


@router.post("/reset-password")
def reset_password_endpoint(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """Reset password with valid token"""
    return reset_password(data.token, data.new_password, db)

