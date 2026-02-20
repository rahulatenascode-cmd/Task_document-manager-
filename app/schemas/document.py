from pydantic import BaseModel
from datetime import datetime
from typing import List


class DocumentResponse(BaseModel):
    id: int
    filename: str
    status: str
    uploaded_at: datetime

    model_config = {
        "from_attributes": True
    }


class PaginatedDocumentResponse(BaseModel):
    total: int
    skip: int
    limit: int
    items: List[DocumentResponse]