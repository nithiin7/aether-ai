"""Document service for managing artifacts."""
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from src.models.document import Document
from src.models.suggestion import Suggestion


class DocumentService:
    """Service for document operations."""

    @staticmethod
    def create_document(
        db: Session, user_id: UUID, title: str, content: str = "", kind: str = "text"
    ) -> Document:
        """
        Create a new document.

        Args:
            db: Database session
            user_id: User ID
            title: Document title
            content: Document content
            kind: Document kind (text/code/image/sheet)

        Returns:
            Created document object
        """
        document = Document(
            id=uuid4(),
            user_id=user_id,
            title=title,
            content=content,
            kind=kind,
            created_at=datetime.utcnow(),
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        return document

    @staticmethod
    def get_document(db: Session, document_id: UUID, user_id: UUID) -> Optional[Document]:
        """
        Get document by ID and verify ownership.

        Args:
            db: Database session
            document_id: Document ID
            user_id: User ID for ownership verification

        Returns:
            Document object or None
        """
        return (
            db.query(Document)
            .filter(Document.id == document_id, Document.user_id == user_id)
            .first()
        )

    @staticmethod
    def update_document(
        db: Session, document_id: UUID, user_id: UUID, content: str
    ) -> Optional[Document]:
        """
        Update document content.

        Args:
            db: Database session
            document_id: Document ID
            user_id: User ID for ownership verification
            content: New content

        Returns:
            Updated document object or None
        """
        document = DocumentService.get_document(db, document_id, user_id)
        if document:
            document.content = content
            document.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(document)
        return document

    @staticmethod
    def get_user_documents(
        db: Session, user_id: UUID, kind: Optional[str] = None, limit: int = 50
    ) -> List[Document]:
        """
        Get user's documents.

        Args:
            db: Database session
            user_id: User ID
            kind: Optional filter by document kind
            limit: Maximum number of documents to return

        Returns:
            List of document objects
        """
        query = db.query(Document).filter(Document.user_id == user_id)

        if kind:
            query = query.filter(Document.kind == kind)

        return query.order_by(Document.updated_at.desc()).limit(limit).all()

    @staticmethod
    def delete_document(db: Session, document_id: UUID, user_id: UUID) -> bool:
        """
        Delete a document.

        Args:
            db: Database session
            document_id: Document ID
            user_id: User ID for ownership verification

        Returns:
            True if deleted, False otherwise
        """
        document = DocumentService.get_document(db, document_id, user_id)
        if document:
            db.delete(document)
            db.commit()
            return True
        return False

    @staticmethod
    def create_suggestion(
        db: Session,
        document_id: UUID,
        user_id: UUID,
        original_text: str,
        suggested_text: str,
        description: Optional[str] = None,
    ) -> Suggestion:
        """
        Create a suggestion for a document.

        Args:
            db: Database session
            document_id: Document ID
            user_id: User ID
            original_text: Original text
            suggested_text: Suggested text
            description: Optional description

        Returns:
            Created suggestion object
        """
        suggestion = Suggestion(
            id=uuid4(),
            document_id=document_id,
            user_id=user_id,
            original_text=original_text,
            suggested_text=suggested_text,
            description=description,
            is_resolved=False,
            created_at=datetime.utcnow(),
        )
        db.add(suggestion)
        db.commit()
        db.refresh(suggestion)
        return suggestion

    @staticmethod
    def get_document_suggestions(
        db: Session, document_id: UUID, include_resolved: bool = False
    ) -> List[Suggestion]:
        """
        Get suggestions for a document.

        Args:
            db: Database session
            document_id: Document ID
            include_resolved: Whether to include resolved suggestions

        Returns:
            List of suggestion objects
        """
        query = db.query(Suggestion).filter(Suggestion.document_id == document_id)

        if not include_resolved:
            query = query.filter(Suggestion.is_resolved == False)

        return query.order_by(Suggestion.created_at.desc()).all()

    @staticmethod
    def resolve_suggestion(db: Session, suggestion_id: UUID) -> bool:
        """
        Mark a suggestion as resolved.

        Args:
            db: Database session
            suggestion_id: Suggestion ID

        Returns:
            True if resolved, False otherwise
        """
        suggestion = db.query(Suggestion).filter(Suggestion.id == suggestion_id).first()
        if suggestion:
            suggestion.is_resolved = True
            db.commit()
            return True
        return False

