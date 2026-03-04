from sqlalchemy.orm import Session
from app.models.user import User
from app.models.password_reset_token import PasswordResetToken, EmailVerificationToken
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token
from app.exceptions.custom_exceptions import BadRequestException, UnauthorizedException, NotFoundException
from app.services.email_service import email_service
from app.utils.token_handler import (
    generate_verification_token,
    generate_verification_link,
    generate_password_reset_link,
    generate_otp,
)
from app.core.config import settings
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def register_user(data, db: Session):
    """Register a new user and send verification email"""
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise BadRequestException("Email already registered")

    # Create new user with unverified status
    user = User(
        email=data.email,
        password=hash_password(data.password),
        is_verified=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Generate OTP and store as verification token
    otp = generate_otp()
    token_obj = EmailVerificationToken.create(
        user_id=user.id,
        token=otp,
        expires_in_minutes=settings.EMAIL_VERIFICATION_OTP_EXPIRE_MINUTES
    )
    db.add(token_obj)
    db.commit()

    # Send OTP via email
    email_service.send_verification_otp_email(user.email, otp)

    return {
        "message": "User registered successfully. Please check your email to verify your account.",
        "user_id": user.id
    }


def verify_email(token: str, db: Session):
    """Verify user email with token"""
    # Find the verification token
    token_obj = db.query(EmailVerificationToken).filter(
        EmailVerificationToken.token == token
    ).first()

    if not token_obj:
        raise BadRequestException("Invalid verification token")

    if not token_obj.is_valid():
        raise BadRequestException("Verification token has expired")

    # Update user verification status
    user = db.query(User).filter(User.id == token_obj.user_id).first()
    if not user:
        raise NotFoundException("User not found")

    user.is_verified = True
    user.verified_at = datetime.utcnow()
    token_obj.used = True

    db.add(user)
    db.add(token_obj)
    db.commit()

    # Send welcome email
    email_service.send_welcome_email(user.email, user.email.split("@")[0])

    return {"message": "Email verified successfully. You can now log in."}


def login_user(data, db: Session):
    """Authenticate user and return tokens"""
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password):
        raise UnauthorizedException("Invalid credentials")

    # Check if email is verified
    # Allow admins to login even if `is_verified` is False (pre-created admin)
    if not user.is_verified and user.role != "admin":
        raise UnauthorizedException("Please verify your email before logging in")

    return {
        "access_token": create_access_token({"user_id": user.id}),
        "refresh_token": create_refresh_token({"user_id": user.id})
    }


def forgot_password(email: str, db: Session):
    """Generate password reset token and send reset email"""
    user = db.query(User).filter(User.email == email).first()

    # Don't reveal if email exists or not for security
    if user:
        # Generate OTP for password reset and store it
        otp = generate_otp()
        token_obj = PasswordResetToken.create(
            user_id=user.id,
            token=otp,
            expires_in_minutes=settings.PASSWORD_RESET_OTP_EXPIRE_MINUTES
        )
        db.add(token_obj)
        db.commit()

        # Send reset OTP email
        email_service.send_password_reset_otp_email(user.email, otp)

    return {"message": "If the email exists, you will receive a password reset code"}


def reset_password(token: str, new_password: str, db: Session):
    """Reset user password with valid token"""
    # Find the reset token
    token_obj = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == token
    ).first()

    if not token_obj:
        raise BadRequestException("Invalid reset token")

    if not token_obj.is_valid():
        raise BadRequestException("Reset token has expired")

    # Update user password
    user = db.query(User).filter(User.id == token_obj.user_id).first()
    if not user:
        raise NotFoundException("User not found")

    user.password = hash_password(new_password)
    token_obj.used = True

    db.add(user)
    db.add(token_obj)
    db.commit()

    return {"message": "Password reset successfully. You can now log in with your new password."}

