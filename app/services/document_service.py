from sqlalchemy.orm import Session
from app.models.document import Document
from app.models.document_status_history import DocumentStatusHistory
from app.exceptions import NotFoundException, InvalidDocumentStatusException, DatabaseException
from app.enums import DocumentStatus


def approve_document(doc_id: int, db: Session):
    try:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            raise NotFoundException(f"Document with ID {doc_id} not found")
        
        if doc.status == DocumentStatus.APPROVED.value:
            raise InvalidDocumentStatusException(doc.status, DocumentStatus.APPROVED.value)

        doc.status = DocumentStatus.APPROVED.value
        db.add(DocumentStatusHistory(
            document_id=doc.id, 
            status=DocumentStatus.APPROVED.value
        ))
        db.commit()
        return {
            "success": True,
            "message": "Document approved successfully",
            "document_id": doc_id,
            "status": DocumentStatus.APPROVED.value
        }
    except Exception as e:
        db.rollback()
        if isinstance(e, (NotFoundException, InvalidDocumentStatusException)):
            raise
        raise DatabaseException(f"Failed to approve document: {str(e)}")


def reject_document(doc_id: int, db: Session, reason: str = None):
    try:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            raise NotFoundException(f"Document with ID {doc_id} not found")
        
        if doc.status == DocumentStatus.REJECTED.value:
            raise InvalidDocumentStatusException(doc.status, DocumentStatus.REJECTED.value)

        doc.status = DocumentStatus.REJECTED.value
        db.add(DocumentStatusHistory(
            document_id=doc.id, 
            status=DocumentStatus.REJECTED.value
        ))
        db.commit()
        return {
            "success": True,
            "message": "Document rejected successfully",
            "document_id": doc_id,
            "status": DocumentStatus.REJECTED.value,
            "reason": reason
        }
    except Exception as e:
        db.rollback()
        if isinstance(e, (NotFoundException, InvalidDocumentStatusException)):
            raise
        raise DatabaseException(f"Failed to reject document: {str(e)}")