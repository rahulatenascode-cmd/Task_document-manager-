import secrets
import string
from app.core.config import settings
from app.core.security import create_access_token as jwt_create_access_token
from datetime import timedelta, datetime


def generate_verification_token() -> str:
    """Generate a secure random verification token"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(64))


def generate_otp(length: int = 6) -> str:
    """Generate a numeric OTP of given length (default 6 digits)."""
    digits = string.digits
    return ''.join(secrets.choice(digits) for _ in range(length))


def generate_verification_link(token: str) -> str:
    """Generate the email verification link"""
    return f"{settings.FRONTEND_URL}/verify-email?token={token}"


def generate_password_reset_link(token: str) -> str:
    """Generate the password reset link"""
    return f"{settings.FRONTEND_URL}/reset-password?token={token}"
