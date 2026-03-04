import os
from fastapi import UploadFile
from app.core.config import settings
from app.exceptions.custom_exceptions import BadRequestException

ALLOWED_TYPES = ["application/pdf", "image/jpeg", "image/png"]

def save_file(file: UploadFile):
    if file.content_type not in ALLOWED_TYPES:
        raise BadRequestException("Invalid file type")

    content = file.file.read()

    if len(content) > settings.MAX_FILE_SIZE:
        raise BadRequestException("File too large")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(settings.UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as f:
        f.write(content)

    return file_path
