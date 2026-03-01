from abc import ABC, abstractmethod
import os
from fastapi import UploadFile
from app.core.config import settings
from app.exceptions.custom_exceptions import BadRequestException


class BaseStorageService(ABC):
    """Abstract interface for file storage backends."""

    @abstractmethod
    def upload(self, file: UploadFile) -> str:
        """Save the provided UploadFile and return a path/URL where it can be retrieved."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, path: str) -> None:
        """Remove a previously stored file given its path/URL."""
        raise NotImplementedError

    @abstractmethod
    def get_url(self, path: str) -> str:
        """Return a public URL for the given stored path. For local storage this may
        simply return the filesystem path or convert to a file:// URL.
        """
        raise NotImplementedError


class LocalStorageService(BaseStorageService):
    """Local filesystem based implementation of storage service."""

    ALLOWED_TYPES = ["application/pdf", "image/jpeg", "image/png"]

    def __init__(self, upload_dir: str = settings.UPLOAD_DIR):
        self.upload_dir = upload_dir
        os.makedirs(self.upload_dir, exist_ok=True)

    def upload(self, file: UploadFile) -> str:
        if file.content_type not in self.ALLOWED_TYPES:
            raise BadRequestException("Invalid file type")

        content = file.file.read()
        if len(content) > settings.MAX_FILE_SIZE:
            raise BadRequestException("File too large")

        file_path = os.path.join(self.upload_dir, file.filename)
        with open(file_path, "wb") as f:
            f.write(content)

        return file_path

    def delete(self, path: str) -> None:
        try:
            os.remove(path)
        except FileNotFoundError:
            pass
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Failed to delete file {path}: {e}")

    def get_url(self, path: str) -> str:
        return path



def get_storage_service() -> BaseStorageService:
    return LocalStorageService()
