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

    REDIS_URL: str = Field("redis://localhost:6379/0", env="REDIS_URL")

    LOG_FILE: str = Field("logs/app.log", env="LOG_FILE")
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

