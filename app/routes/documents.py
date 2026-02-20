from fastapi import APIRouter, Depends, UploadFile, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.dependencies.auth import get_db, get_current_user, admin_only
from app.utils.file_handler import save_file
from app.models.document import Document
from app.services.document_service import approve_document, reject_document
from app.schemas.document import DocumentResponse, PaginatedDocumentResponse
from app.enums import DocumentStatus
from app.exceptions import FileUploadException, NotFoundException

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post("/upload")
def upload_document(file: UploadFile,
                    db: Session = Depends(get_db),
                    user=Depends(get_current_user)):
    try:
        if not file.filename:
            raise FileUploadException("File must have a filename")
        
        path = save_file(file)

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
    result = approve_document(doc_id, db)
    bg.add_task(print, f"Document {doc_id} approved by admin")
    return result

@router.post("/{doc_id}/reject")
def reject(doc_id: int,
           reason: Optional[str] = Query(None),
           bg: BackgroundTasks = BackgroundTasks(),
           db: Session = Depends(get_db),
           admin=Depends(admin_only)):
    result = reject_document(doc_id, db, reason)
    bg.add_task(print, f"Document {doc_id} rejected by admin with reason: {reason}")
    return result

@router.get("/public", response_model=PaginatedDocumentResponse)
def public_documents(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None)):
    
    query = db.query(Document).filter(Document.status == DocumentStatus.APPROVED.value)
    
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

@router.get("/", response_model=PaginatedDocumentResponse)
def list_documents(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None)):
    
    query = db.query(Document).filter(Document.uploaded_by == user.id)
    
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
    doc = db.query(Document).filter(Document.id == doc_id).first()
    
    if not doc:
        raise NotFoundException(f"Document with ID {doc_id} not found")
    
    if doc.uploaded_by != user.id and not admin_only:
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
    doc = db.query(Document).filter(Document.id == doc_id).first()
    
    if not doc:
        raise NotFoundException(f"Document with ID {doc_id} not found")
    
    if doc.uploaded_by != user.id:
        raise NotFoundException("Can only delete your own documents")
    
    if doc.status != DocumentStatus.PENDING.value:
        raise FileUploadException("Can only delete pending documents")
    
    db.delete(doc)
    db.commit()
    
    return {
        "success": True,
        "message": "Document deleted successfully",
        "document_id": doc_id
    }