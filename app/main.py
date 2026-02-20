from fastapi import FastAPI
from app.routes import auth, documents
from app.core.database import Base, engine
from app.exceptions import (
    app_exception_handler,
    validation_exception_handler,
    sqlalchemy_exception_handler,
    generic_exception_handler,
)
from app.exceptions.custom_exceptions import AppException
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Document Management API",
    description="Professional document management system with authentication and file handling",
    version="1.0.0"
)

app.include_router(auth.router)
app.include_router(documents.router)

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "success": True,
        "status": "healthy",
        "service": "Document Management API"
    }