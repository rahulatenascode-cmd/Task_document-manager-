from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime
from app.core.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    filename = Column(String(255))
    file_path = Column(String(255))
    status = Column(String(20), default="pending")
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    uploaded_by = Column(Integer, ForeignKey("users.id"))