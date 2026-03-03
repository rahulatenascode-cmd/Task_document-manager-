from sqlalchemy.orm import Session
from app.models.document import Document
from app.models.document_status_history import DocumentStatusHistory
from app.exceptions import NotFoundException, InvalidDocumentStatusException, DatabaseException
from app.enums import DocumentStatus
from datetime import datetime
from app.core import cache
from app.services.storage import get_storage_service


def mark_document_deleted(doc: Document, db: Session, user_id: int = None, reason: str = None):
    """Perform a soft delete by setting flags on the document record and log history.
    Also attempt to remove the underlying file from the storage backend and clear
    relevant caches.
    """
    doc.is_deleted = True
    doc.deleted_at = datetime.utcnow()
    db.add(doc)
    hist = DocumentStatusHistory(
        document_id=doc.id,
        status="deleted",
        changed_by=user_id,
        reason=reason,
    )
    db.add(hist)
    db.commit()

    try:
        storage = get_storage_service()
        storage.delete(doc.file_path)
    except Exception:
        pass

    cache.invalidate_prefix("approved_docs")
    cache.invalidate_prefix("admin_stats")

    return doc


def approve_document(doc_id: int, db: Session, user_id: int = None, reason: str = None):
    try:
        doc = db.query(Document).filter(Document.id == doc_id, Document.is_deleted == False).first()
        if not doc:
            raise NotFoundException(f"Document with ID {doc_id} not found")
        
        if doc.status == DocumentStatus.APPROVED.value:
            raise InvalidDocumentStatusException(doc.status, DocumentStatus.APPROVED.value)

        doc.status = DocumentStatus.APPROVED.value
        history = DocumentStatusHistory(
            document_id=doc.id,
            status=DocumentStatus.APPROVED.value,
            changed_by=user_id,
            reason=reason,
        )
        db.add(history)
        db.commit()
        cache.invalidate_prefix("approved_docs")
        cache.delete_cache("admin_stats")
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


def reject_document(doc_id: int, db: Session, user_id: int = None, reason: str = None):
    try:
        doc = db.query(Document).filter(Document.id == doc_id, Document.is_deleted == False).first()
        if not doc:
            raise NotFoundException(f"Document with ID {doc_id} not found")
        
        if doc.status == DocumentStatus.REJECTED.value:
            raise InvalidDocumentStatusException(doc.status, DocumentStatus.REJECTED.value)

        doc.status = DocumentStatus.REJECTED.value
        history = DocumentStatusHistory(
            document_id=doc.id,
            status=DocumentStatus.REJECTED.value,
            changed_by=user_id,
            reason=reason,
        )
        db.add(history)
        db.commit()
        cache.invalidate_prefix("approved_docs")
        cache.delete_cache("admin_stats")
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
