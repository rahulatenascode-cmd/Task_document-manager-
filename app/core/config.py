from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):




    SECRET_KEY: str = Field(..., env="SECRET_KEY")




    ALGORITHM: str = Field("HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7






    DATABASE_URL: str = Field(..., env="DATABASE_URL")

    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 5 * 1024 * 1024

    # Email Configuration
    MAIL_HOST: str = Field(..., env="MAIL_HOST")
    MAIL_PORT: int = Field(..., env="MAIL_PORT")
    MAIL_USERNAME: str = Field(..., env="MAIL_USERNAME")
    MAIL_PASSWORD: str = Field(..., env="MAIL_PASSWORD")
    MAIL_FROM: str = Field(..., env="MAIL_FROM")
    MAIL_DISPLAY_NAME: str = Field("Service", env="MAIL_DISPLAY_NAME")
    MAIL_SMTP_AUTH: bool = Field(True, env="MAIL_SMTP_AUTH")
    MAIL_STARTTLS_ENABLE: bool = Field(True, env="MAIL_STARTTLS_ENABLE")
    MAIL_DEFAULT_ENCODING: str = Field("UTF-8", env="MAIL_DEFAULT_ENCODING")

    # Token Expiry
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = Field(30, env="PASSWORD_RESET_TOKEN_EXPIRE_MINUTES")
    EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES: int = Field(1440, env="EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES")
    # OTP expiry for email verification (minutes)
    EMAIL_VERIFICATION_OTP_EXPIRE_MINUTES: int = Field(10, env="EMAIL_VERIFICATION_OTP_EXPIRE_MINUTES")
    # OTP expiry for password reset (minutes)
    PASSWORD_RESET_OTP_EXPIRE_MINUTES: int = Field(30, env="PASSWORD_RESET_OTP_EXPIRE_MINUTES")

    # Frontend URL
    FRONTEND_URL: str = Field("http://localhost:3000", env="FRONTEND_URL")

    REDIS_URL: str = Field("redis://localhost:6379/0", env="REDIS_URL")


    LOG_FILE: str = Field("logs/app.log", env="LOG_FILE")
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
