from typing import Optional, Dict, Any


class AppException(Exception):
    
    def __init__(
        self, 
        message: str, 
        status_code: int,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)


class BadRequestException(AppException):
    
    def __init__(
        self, 
        message: str = "Bad Request",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, 400, "BAD_REQUEST", details)


class UnauthorizedException(AppException):
    
    def __init__(self, message: str = "Unauthorized - Please provide valid credentials"):
        super().__init__(message, 401, "UNAUTHORIZED")


class ForbiddenException(AppException):
    
    def __init__(self, message: str = "Forbidden - You do not have permission"):
        super().__init__(message, 403, "FORBIDDEN")


class NotFoundException(AppException):
    
    def __init__(self, message: str = "Not Found"):
        super().__init__(message, 404, "NOT_FOUND")


class ConflictException(AppException):
    
    def __init__(
        self, 
        message: str = "Conflict - Resource already exists",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, 409, "CONFLICT", details)


class UnprocessableEntityException(AppException):
    
    def __init__(
        self, 
        message: str = "Unprocessable Entity",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, 422, "UNPROCESSABLE_ENTITY", details)


class InternalServerException(AppException):
    
    def __init__(self, message: str = "Internal Server Error"):
        super().__init__(message, 500, "INTERNAL_SERVER_ERROR")


class ServiceUnavailableException(AppException):
    
    def __init__(self, message: str = "Service Unavailable"):
        super().__init__(message, 503, "SERVICE_UNAVAILABLE")


class DocumentException(AppException):
    
    def __init__(
        self,
        message: str,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, status_code, "DOCUMENT_ERROR", details)


class InvalidDocumentStatusException(AppException):
    
    def __init__(
        self,
        current_status: str,
        requested_status: str
    ):
        message = f"Cannot transition from '{current_status}' to '{requested_status}'"
        details = {"current_status": current_status, "requested_status": requested_status}
        super().__init__(message, 400, "INVALID_STATUS_TRANSITION", details)


class FileUploadException(AppException):
    
    def __init__(
        self,
        message: str = "File upload failed",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, 400, "FILE_UPLOAD_ERROR", details)


class InvalidFileTypeException(AppException):
    
    def __init__(
        self,
        file_type: str,
        allowed_types: list
    ):
        message = f"File type '{file_type}' not allowed"
        details = {"uploaded_type": file_type, "allowed_types": allowed_types}
        super().__init__(message, 400, "INVALID_FILE_TYPE", details)


class FileSizeException(AppException):
    
    def __init__(
        self,
        file_size: int,
        max_size: int
    ):
        message = f"File size {file_size} bytes exceeds maximum {max_size} bytes"
        details = {"file_size": file_size, "max_size": max_size}
        super().__init__(message, 413, "FILE_SIZE_EXCEEDED", details)


class DatabaseException(AppException):
    
    def __init__(
        self,
        message: str = "Database operation failed",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, 500, "DATABASE_ERROR", details)


class DuplicateResourceException(AppException):
    
    def __init__(
        self,
        resource_type: str,
        field: str,
        value: str
    ):
        message = f"{resource_type} with {field}='{value}' already exists"
        details = {"resource_type": resource_type, "field": field, "value": value}
        super().__init__(message, 409, "DUPLICATE_RESOURCE", details)
