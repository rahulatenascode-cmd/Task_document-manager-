class Settings:
    SECRET_KEY = "supersecretkey"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    REFRESH_TOKEN_EXPIRE_DAYS = 7

    DATABASE_URL = "mysql+pymysql://root:Rahul315%40@localhost:3306/document_db"

    UPLOAD_DIR = "uploads"
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

settings = Settings()