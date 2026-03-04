from fastapi.responses import JSONResponse
import logging
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from app.exceptions.custom_exceptions import AppException
from typing import Dict, Any

logger = logging.getLogger(__name__)


def create_error_response(
    status_code: int,
    message: str,
    error_code: str = "ERROR",
    details: Dict[str, Any] = None,
    validation_errors: list = None
) -> Dict[str, Any]:
    response = {
        "success": False,
        "error": {
            "status_code": status_code,
            "error_code": error_code,
            "message": message,
        }
    }
    
    if details:
        response["error"]["details"] = details
    
    if validation_errors:
        response["error"]["validation_errors"] = validation_errors
    
    return response


async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            status_code=exc.status_code,
            message=exc.message,
            error_code=exc.error_code,
            details=exc.details if exc.details else None
        )
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(x) for x in error["loc"][1:]),
            "type": error["type"],
            "message": error["msg"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=create_error_response(
            status_code=422,
            message="Validation Error - Invalid request parameters",
            error_code="VALIDATION_ERROR",
            validation_errors=errors
        )
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    error_msg = str(exc)
    
    logger.error(f"Database Error: {error_msg}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=create_error_response(
            status_code=500,
            message="Database operation failed",
            error_code="DATABASE_ERROR"
        )
    )


async def generic_exception_handler(request: Request, exc: Exception):
    error_msg = str(exc)
    
    logger.error(f"Unexpected Error: {error_msg}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=create_error_response(
            status_code=500,
            message="An unexpected error occurred",
            error_code="INTERNAL_SERVER_ERROR"
        )
    )
