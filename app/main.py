from fastapi import FastAPI
from app.routes import auth, documents
from app.core.database import Base, engine
from app.models import user, document, document_status_history, password_reset_token
from app.exceptions import (
    app_exception_handler,
    validation_exception_handler,
    sqlalchemy_exception_handler,
    generic_exception_handler,
)
from app.exceptions.custom_exceptions import AppException
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import inspect, text
import logging
import os
from app.core.config import settings
import time
from datetime import datetime
from sqlalchemy.exc import OperationalError
from app.core import cache

logger = logging.getLogger(__name__)

log_dir = os.path.dirname(settings.LOG_FILE)
if log_dir:
    os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(settings.LOG_FILE)
    ]
)

def _ensure_schema():
    """Add missing columns for existing databases.

    This helper checks for the new fields that were introduced in recent updates.
    If they are absent, ALTER TABLE statements are executed to add them.
    Using a full migration tool like Alembic is recommended for production
    but this simple routine eases development.
    """

    insp = inspect(engine)
    with engine.connect() as conn:
        if "documents" in insp.get_table_names():
            cols = [c["name"] for c in insp.get_columns("documents")]
            if "is_deleted" not in cols:
                logger.info("Adding is_deleted column to documents table")
                conn.execute(text("ALTER TABLE documents ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE"))
            if "deleted_at" not in cols:
                logger.info("Adding deleted_at column to documents table")
                conn.execute(text("ALTER TABLE documents ADD COLUMN deleted_at DATETIME NULL"))

        if "document_status_history" in insp.get_table_names():
            cols = [c["name"] for c in insp.get_columns("document_status_history")]
            if "changed_by" not in cols:
                logger.info("Adding changed_by column to document_status_history")
                conn.execute(text("ALTER TABLE document_status_history ADD COLUMN changed_by INT NULL"))
            if "reason" not in cols:
                logger.info("Adding reason column to document_status_history")
                conn.execute(text("ALTER TABLE document_status_history ADD COLUMN reason VARCHAR(500) NULL"))

        # Email verification columns for users table
        if "users" in insp.get_table_names():
            cols = [c["name"] for c in insp.get_columns("users")]
            if "is_verified" not in cols:
                logger.info("Adding is_verified column to users table")
                conn.execute(text("ALTER TABLE users ADD COLUMN is_verified BOOLEAN DEFAULT FALSE"))
            if "verified_at" not in cols:
                logger.info("Adding verified_at column to users table")
                conn.execute(text("ALTER TABLE users ADD COLUMN verified_at DATETIME NULL"))
            if "created_at" not in cols:
                logger.info("Adding created_at column to users table")
                conn.execute(text("ALTER TABLE users ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP"))

try:
    Base.metadata.create_all(bind=engine)
    _ensure_schema()
except SQLAlchemyError as e:
    logger.warning(f"Could not initialize database: {e}. API will still run but database operations may fail.")
except Exception as e:
    logger.warning(f"Error initializing database: {e}. API will still run but database operations may fail.")


_app_start_time = datetime.utcnow()

app = FastAPI(
    title="Document Management API",
    description="Professional document management system with authentication and file handling",
    version="1.0.0"
)

from fastapi import APIRouter

v1 = APIRouter(prefix="/api/v1")
v1.include_router(auth.router)
v1.include_router(documents.router)

app.include_router(v1)

@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url.path}")
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    logger.info(f"Completed {request.method} {request.url.path} with status {response.status_code} in {duration:.3f}s")
    return response

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)


@app.on_event("startup")
def startup_tasks():
    try:
        cache.get_redis()
        logger.info("Connected to Redis cache")
    except Exception as e:
        logger.warning(f"Could not connect to Redis: {e}. Caching will be disabled.")

@app.get("/api/v1/health", tags=["Health"])
def health_check():
    """Basic readiness probe used by load‑balancers and orchestrators."""
    db_status = "unknown"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        logger.error(f"Health check DB connectivity failure: {e}")
        db_status = "unavailable"

    uptime = datetime.utcnow() - _app_start_time
    return {
        "success": True,
        "status": "healthy" if db_status == "connected" else "degraded",
        "service": "Document Management API",
        "database": db_status,
        "uptime_seconds": int(uptime.total_seconds())
    }
