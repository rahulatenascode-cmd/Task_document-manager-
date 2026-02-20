from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime
from app.core.database import Base

class DocumentStatusHistory(Base):
    __tablename__ = "document_status_history"

    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    status = Column(String(20))
    changed_at = Column(DateTime, default=datetime.utcnow)