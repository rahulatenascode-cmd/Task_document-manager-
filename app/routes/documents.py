from fastapi import APIRouter, Depends, UploadFile, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.dependencies.auth import get_db, get_current_user, admin_only
from app.services.storage import get_storage_service, BaseStorageService
from app.models.document import Document
from app.services.document_service import approve_document, reject_document
from app.schemas.document import DocumentResponse, PaginatedDocumentResponse, StatsResponse
from app.enums import DocumentStatus
from app.exceptions import FileUploadException, NotFoundException
from app.core import cache

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post("/upload")
def upload_document(
    file: UploadFile,
    storage: BaseStorageService = Depends(get_storage_service),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Receives an UploadFile, stores it via the configured storage backend,
    and records a Document row. Business logic is kept out of main.
    """
    try:
        if not file.filename:
            raise FileUploadException("File must have a filename")


        path = storage.upload(file)

        doc = Document(
            filename=file.filename,
            file_path=path,
            uploaded_by=user.id,
            status=DocumentStatus.PENDING.value
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)

        return {
            "success": True,
            "message": "Document uploaded successfully",
            "document_id": doc.id,
            "filename": doc.filename,
            "status": doc.status
        }
    except FileUploadException:
        raise
    except Exception as e:
        db.rollback()
        raise FileUploadException(f"Upload failed: {str(e)}")

@router.post("/{doc_id}/approve")
def approve(doc_id: int,
            bg: BackgroundTasks,
            db: Session = Depends(get_db),
            admin=Depends(admin_only)):
    result = approve_document(doc_id, db, user_id=admin.id)

    from app.main import logger
    bg.add_task(logger.info, f"Document {doc_id} approved by admin {admin.id}")
    return result

@router.post("/{doc_id}/reject")
def reject(doc_id: int,
           reason: Optional[str] = Query(None),
           bg: BackgroundTasks = BackgroundTasks(),
           db: Session = Depends(get_db),
           admin=Depends(admin_only)):
    result = reject_document(doc_id, db, user_id=admin.id, reason=reason)
    from app.main import logger
    bg.add_task(logger.info, f"Document {doc_id} rejected by admin {admin.id} with reason: {reason}")
    return result

@router.get("/public", response_model=PaginatedDocumentResponse)
def public_documents(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None)):

    cache_key = f"approved_docs:{skip}:{limit}:{search or ''}:{status or ''}"
    cached = cache.get_cache(cache_key)
    if cached is not None:
        return cached

    query = db.query(Document).filter(
        Document.status == DocumentStatus.APPROVED.value,
        Document.is_deleted == False
    )
    
    if search:
        query = query.filter(Document.filename.ilike(f"%{search}%"))
    
    if status:
        query = query.filter(Document.status == status)
    
    total = query.count()
    documents = query.offset(skip).limit(limit).all()
    result = {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": documents
    }

    cache.set_cache(cache_key, result, ex=60)
    return result

@router.get("/", response_model=PaginatedDocumentResponse)
def list_documents(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None)):
    
    query = db.query(Document).filter(
        Document.uploaded_by == user.id,
        Document.is_deleted == False
    )
    
    if search:
        query = query.filter(Document.filename.ilike(f"%{search}%"))
    
    if status:
        query = query.filter(Document.status == status)
    
    total = query.count()
    documents = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": documents
    }

@router.get("/{doc_id}")
def get_document(
    doc_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)):
    doc = db.query(Document).filter(Document.id == doc_id, Document.is_deleted == False).first()
    
    if not doc:
        raise NotFoundException(f"Document with ID {doc_id} not found")
    

    if doc.uploaded_by != user.id and user.role != "admin":
        raise NotFoundException("Access denied")
    
    return {
        "success": True,
        "data": {
            "id": doc.id,
            "filename": doc.filename,
            "status": doc.status,
            "uploaded_at": doc.uploaded_at,
            "uploaded_by": doc.uploaded_by
        }
    }

@router.delete("/{doc_id}")
def delete_document(
    doc_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)):
    doc = db.query(Document).filter(Document.id == doc_id, Document.is_deleted == False).first()
    
    if not doc:
        raise NotFoundException(f"Document with ID {doc_id} not found")
    

    is_owner = doc.uploaded_by == user.id
    is_admin = user.role == "admin"
    
    if not (is_owner or is_admin):
        raise NotFoundException("Access denied - Can only delete your own documents or admin can delete any document")
    
    if doc.status != DocumentStatus.PENDING.value:
        raise FileUploadException("Can only delete pending documents")
    

    from app.services.document_service import mark_document_deleted
    mark_document_deleted(doc, db, user_id=user.id, reason="soft delete by user")
    
    return {
        "success": True,
        "message": "Document deleted successfully",
        "document_id": doc_id
    }

@router.get("/admin/stats", response_model=StatsResponse)
def admin_stats(
    db: Session = Depends(get_db),
    admin=Depends(admin_only),
):
    """Return basic counts for dashboard; result is cached."""
    cache_key = "admin_stats"
    cached = cache.get_cache(cache_key)
    if cached is not None:
        return cached

    total = db.query(Document).filter(Document.is_deleted == False).count()
    approved = db.query(Document).filter(
        Document.status == DocumentStatus.APPROVED.value,
        Document.is_deleted == False
    ).count()
    pending = db.query(Document).filter(
        Document.status == DocumentStatus.PENDING.value,
        Document.is_deleted == False
    ).count()
    rejected = db.query(Document).filter(
        Document.status == DocumentStatus.REJECTED.value,
        Document.is_deleted == False
    ).count()

    stats = {
        "total_documents": total,
        "approved": approved,
        "pending": pending,
        "rejected": rejected
    }
    cache.set_cache(cache_key, stats, ex=60)
    return stats

@router.get("/{doc_id}/download")
def download_document(
    doc_id: int,
    storage: BaseStorageService = Depends(get_storage_service),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Stream an approved document if the requester has permission."""
    doc = db.query(Document).filter(
        Document.id == doc_id,
        Document.status == DocumentStatus.APPROVED.value,
        Document.is_deleted == False
    ).first()
    if not doc:
        raise NotFoundException(f"Document with ID {doc_id} not found or not available")

    if doc.uploaded_by != user.id and user.role != "admin":
        raise NotFoundException("Access denied")

    from fastapi.responses import FileResponse
    file_path = storage.get_url(doc.file_path)
    return FileResponse(path=file_path, filename=doc.filename)
