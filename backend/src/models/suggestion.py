"""Suggestion model definition."""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Text, UUID
from sqlalchemy.orm import relationship

from src.config.database import Base


class Suggestion(Base):
    """Suggestion model for document edits."""

    __tablename__ = "suggestions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    original_text = Column(Text, nullable=False)
    suggested_text = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    is_resolved = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    document = relationship("Document", back_populates="suggestions")

    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            "id": str(self.id),
            "document_id": str(self.document_id),
            "user_id": str(self.user_id),
            "original_text": self.original_text,
            "suggested_text": self.suggested_text,
            "description": self.description,
            "is_resolved": self.is_resolved,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        """String representation."""
        return f"<Suggestion {self.id}>"

