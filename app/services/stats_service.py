"""
Document Statistics - Display approved, rejected, and pending documents
Run this file directly to view document status statistics from the database
"""

import sys
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime


sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.core.database import SessionLocal
from app.models.document import Document
from app.enums import DocumentStatus


class DocumentStats:
    """Display document statistics from database"""
    
    def __init__(self):
        self.db = SessionLocal()
    
    def close(self):
        """Close database connection"""
        self.db.close()
    
    def get_status_counts(self):
        """Get count of documents by status"""
        try:
            stats = {}
            

            approved = self.db.query(func.count(Document.id)).filter(
                and_(
                    Document.status == DocumentStatus.APPROVED.value,
                    Document.is_deleted == False
                )
            ).scalar()
            

            rejected = self.db.query(func.count(Document.id)).filter(
                and_(
                    Document.status == DocumentStatus.REJECTED.value,
                    Document.is_deleted == False
                )
            ).scalar()
            

            pending = self.db.query(func.count(Document.id)).filter(
                and_(
                    Document.status == DocumentStatus.PENDING.value,
                    Document.is_deleted == False
                )
            ).scalar()
            

            total = self.db.query(func.count(Document.id)).filter(
                Document.is_deleted == False
            ).scalar()
            
            stats = {
                "approved": approved or 0,
                "rejected": rejected or 0,
                "pending": pending or 0,
                "total": total or 0
            }
            
            return stats
        except Exception as e:
            print(f"❌ Error fetching statistics: {str(e)}")
            return None
    
    def get_approved_documents(self, limit=10):
        """Get list of approved documents"""
        try:
            documents = self.db.query(Document).filter(
                and_(
                    Document.status == DocumentStatus.APPROVED.value,
                    Document.is_deleted == False
                )
            ).order_by(Document.uploaded_at.desc()).limit(limit).all()
            
            return documents
        except Exception as e:
            print(f"❌ Error fetching approved documents: {str(e)}")
            return []
    
    def get_rejected_documents(self, limit=10):
        """Get list of rejected documents"""
        try:
            documents = self.db.query(Document).filter(
                and_(
                    Document.status == DocumentStatus.REJECTED.value,
                    Document.is_deleted == False
                )
            ).order_by(Document.uploaded_at.desc()).limit(limit).all()
            
            return documents
        except Exception as e:
            print(f"❌ Error fetching rejected documents: {str(e)}")
            return []
    
    def get_pending_documents(self, limit=10):
        """Get list of pending documents"""
        try:
            documents = self.db.query(Document).filter(
                and_(
                    Document.status == DocumentStatus.PENDING.value,
                    Document.is_deleted == False
                )
            ).order_by(Document.uploaded_at.desc()).limit(limit).all()
            
            return documents
        except Exception as e:
            print(f"❌ Error fetching pending documents: {str(e)}")
            return []
    
    def display_stats(self):
        """Display statistics in console"""
        print("\n" + "="*60)
        print("📊 DOCUMENT STATISTICS")
        print("="*60)
        
        stats = self.get_status_counts()
        
        if stats:
            print(f"\n✅ APPROVED:  {stats['approved']:5d}")
            print(f"❌ REJECTED:  {stats['rejected']:5d}")
            print(f"⏳ PENDING:   {stats['pending']:5d}")
            print(f"📈 TOTAL:    {stats['total']:5d}")
            print(f"\n📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return stats
    
    def display_approved_docs(self):
        """Display approved documents"""
        print("\n" + "="*60)
        print("✅ APPROVED DOCUMENTS")
        print("="*60)
        
        docs = self.get_approved_documents()
        
        if docs:
            for idx, doc in enumerate(docs, 1):
                print(f"\n{idx}. ID: {doc.id}")
                print(f"   Filename: {doc.filename}")
                print(f"   Uploaded: {doc.uploaded_at.strftime('%Y-%m-%d %H:%M:%S') if doc.uploaded_at else 'N/A'}")
                print(f"   Uploaded By: {doc.uploaded_by}")
        else:
            print("\n   No approved documents found.")
    
    def display_rejected_docs(self):
        """Display rejected documents"""
        print("\n" + "="*60)
        print("❌ REJECTED DOCUMENTS")
        print("="*60)
        
        docs = self.get_rejected_documents()
        
        if docs:
            for idx, doc in enumerate(docs, 1):
                print(f"\n{idx}. ID: {doc.id}")
                print(f"   Filename: {doc.filename}")
                print(f"   Uploaded: {doc.uploaded_at.strftime('%Y-%m-%d %H:%M:%S') if doc.uploaded_at else 'N/A'}")
                print(f"   Uploaded By: {doc.uploaded_by}")
        else:
            print("\n   No rejected documents found.")
    
    def display_pending_docs(self):
        """Display pending documents"""
        print("\n" + "="*60)
        print("⏳ PENDING DOCUMENTS")
        print("="*60)
        
        docs = self.get_pending_documents()
        
        if docs:
            for idx, doc in enumerate(docs, 1):
                print(f"\n{idx}. ID: {doc.id}")
                print(f"   Filename: {doc.filename}")
                print(f"   Uploaded: {doc.uploaded_at.strftime('%Y-%m-%d %H:%M:%S') if doc.uploaded_at else 'N/A'}")
                print(f"   Uploaded By: {doc.uploaded_by}")
        else:
            print("\n   No pending documents found.")
    
    def display_all(self):
        """Display all statistics and documents"""
        self.display_stats()
        self.display_approved_docs()
        self.display_rejected_docs()
        self.display_pending_docs()
        print("\n" + "="*60 + "\n")


def main():
    """Main entry point"""
    print("\n🔌 Connecting to database...")
    
    try:
        stats = DocumentStats()
        stats.display_all()
        stats.close()
        print("✓ Database connection closed.")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
