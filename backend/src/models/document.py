"""Document model definition."""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, String, Text, UUID
from sqlalchemy.orm import relationship

from src.config.database import Base


class Document(Base):
    """Document model representing an artifact."""

    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=True)
    kind = Column(String(20), default="text", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    suggestions = relationship(
        "Suggestion", back_populates="document", cascade="all, delete-orphan"
    )

    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "title": self.title,
            "content": self.content,
            "kind": self.kind,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:
        """String representation."""
        return f"<Document {self.id} - {self.title}>"

