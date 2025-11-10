"""Chat service for managing conversations."""
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from src.models.chat import Chat
from src.models.message import Message


class ChatService:
    """Service for chat operations."""

    @staticmethod
    def create_chat(
        db: Session, user_id: UUID, title: str, visibility: str = "private"
    ) -> Chat:
        """
        Create a new chat.

        Args:
            db: Database session
            user_id: User ID
            title: Chat title
            visibility: Chat visibility (public/private)

        Returns:
            Created chat object
        """
        chat = Chat(
            id=uuid4(), user_id=user_id, title=title, visibility=visibility, created_at=datetime.utcnow()
        )
        db.add(chat)
        db.commit()
        db.refresh(chat)
        return chat

    @staticmethod
    def get_chat(db: Session, chat_id: UUID, user_id: UUID) -> Optional[Chat]:
        """
        Get chat by ID and verify ownership.

        Args:
            db: Database session
            chat_id: Chat ID
            user_id: User ID for ownership verification

        Returns:
            Chat object or None
        """
        return db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == user_id).first()

    @staticmethod
    def get_user_chats(db: Session, user_id: UUID, limit: int = 50) -> List[Chat]:
        """
        Get user's chat list.

        Args:
            db: Database session
            user_id: User ID
            limit: Maximum number of chats to return

        Returns:
            List of chat objects
        """
        return (
            db.query(Chat)
            .filter(Chat.user_id == user_id)
            .order_by(Chat.updated_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def delete_chat(db: Session, chat_id: UUID, user_id: UUID) -> bool:
        """
        Delete a chat.

        Args:
            db: Database session
            chat_id: Chat ID
            user_id: User ID for ownership verification

        Returns:
            True if deleted, False otherwise
        """
        chat = ChatService.get_chat(db, chat_id, user_id)
        if chat:
            db.delete(chat)
            db.commit()
            return True
        return False

    @staticmethod
    def update_chat_context(db: Session, chat_id: UUID, context: dict) -> bool:
        """
        Update chat's last context (usage info).

        Args:
            db: Database session
            chat_id: Chat ID
            context: Context data (usage, model info, etc.)

        Returns:
            True if updated, False otherwise
        """
        chat = db.query(Chat).filter(Chat.id == chat_id).first()
        if chat:
            chat.last_context = context
            chat.updated_at = datetime.utcnow()
            db.commit()
            return True
        return False

    @staticmethod
    def add_message(
        db: Session,
        chat_id: UUID,
        role: str,
        parts: list,
        attachments: Optional[list] = None,
    ) -> Message:
        """
        Add a message to a chat.

        Args:
            db: Database session
            chat_id: Chat ID
            role: Message role (user/assistant)
            parts: Message parts
            attachments: Optional attachments

        Returns:
            Created message object
        """
        message = Message(
            id=uuid4(),
            chat_id=chat_id,
            role=role,
            parts=parts,
            attachments=attachments or [],
            created_at=datetime.utcnow(),
        )
        db.add(message)
        
        # Update chat's updated_at timestamp
        chat = db.query(Chat).filter(Chat.id == chat_id).first()
        if chat:
            chat.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(message)
        return message

    @staticmethod
    def get_messages(db: Session, chat_id: UUID, limit: int = 100) -> List[Message]:
        """
        Get messages for a chat.

        Args:
            db: Database session
            chat_id: Chat ID
            limit: Maximum number of messages to return

        Returns:
            List of message objects
        """
        return (
            db.query(Message)
            .filter(Message.chat_id == chat_id)
            .order_by(Message.created_at.asc())
            .limit(limit)
            .all()
        )

