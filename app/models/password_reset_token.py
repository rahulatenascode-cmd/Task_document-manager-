from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from app.core.database import Base
from datetime import datetime, timedelta

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False, nullable=False)

    @classmethod
    def create(cls, user_id: int, token: str, expires_in_minutes: int = 30):
        """Create a new password reset token"""
        now = datetime.utcnow()
        return cls(
            user_id=user_id,
            token=token,
            created_at=now,
            expires_at=now + timedelta(minutes=expires_in_minutes),
            used=False
        )

    def is_valid(self) -> bool:
        """Check if token is still valid"""
        return not self.used and datetime.utcnow() < self.expires_at


class EmailVerificationToken(Base):
    __tablename__ = "email_verification_tokens"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False, nullable=False)

    @classmethod
    def create(cls, user_id: int, token: str, expires_in_minutes: int = 1440):
        """Create a new email verification token"""
        now = datetime.utcnow()
        return cls(
            user_id=user_id,
            token=token,
            created_at=now,
            expires_at=now + timedelta(minutes=expires_in_minutes),
            used=False
        )

    def is_valid(self) -> bool:
        """Check if token is still valid"""
        return not self.used and datetime.utcnow() < self.expires_at
