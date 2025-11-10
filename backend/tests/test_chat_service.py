"""Tests for chat service."""
import pytest
from uuid import uuid4
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config.database import Base
from src.models.chat import Chat
from src.models.message import Message
from src.services.chat_service import ChatService


@pytest.fixture
def db_session():
    """Create test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


class TestChatService:
    """Test chat service."""

    def test_create_chat(self, db_session):
        """Test chat creation."""
        user_id = uuid4()
        chat = ChatService.create_chat(db_session, user_id, "Test Chat", "private")

        assert chat is not None
        assert chat.user_id == user_id
        assert chat.title == "Test Chat"
        assert chat.visibility == "private"

    def test_get_chat(self, db_session):
        """Test getting chat by ID."""
        user_id = uuid4()
        chat = ChatService.create_chat(db_session, user_id, "Test Chat", "private")

        retrieved = ChatService.get_chat(db_session, chat.id, user_id)
        assert retrieved is not None
        assert retrieved.id == chat.id
        assert retrieved.title == chat.title

    def test_get_chat_wrong_user(self, db_session):
        """Test getting chat with wrong user ID."""
        user_id = uuid4()
        wrong_user_id = uuid4()
        chat = ChatService.create_chat(db_session, user_id, "Test Chat", "private")

        retrieved = ChatService.get_chat(db_session, chat.id, wrong_user_id)
        assert retrieved is None

    def test_delete_chat(self, db_session):
        """Test chat deletion."""
        user_id = uuid4()
        chat = ChatService.create_chat(db_session, user_id, "Test Chat", "private")

        deleted = ChatService.delete_chat(db_session, chat.id, user_id)
        assert deleted is True

        retrieved = ChatService.get_chat(db_session, chat.id, user_id)
        assert retrieved is None

    def test_add_message(self, db_session):
        """Test adding message to chat."""
        user_id = uuid4()
        chat = ChatService.create_chat(db_session, user_id, "Test Chat", "private")

        message = ChatService.add_message(
            db_session,
            chat.id,
            "user",
            [{"type": "text", "text": "Hello"}],
            []
        )

        assert message is not None
        assert message.chat_id == chat.id
        assert message.role == "user"
        assert len(message.parts) == 1

    def test_get_messages(self, db_session):
        """Test getting chat messages."""
        user_id = uuid4()
        chat = ChatService.create_chat(db_session, user_id, "Test Chat", "private")

        # Add messages
        ChatService.add_message(
            db_session, chat.id, "user", [{"type": "text", "text": "Hello"}], []
        )
        ChatService.add_message(
            db_session, chat.id, "assistant", [{"type": "text", "text": "Hi!"}], []
        )

        messages = ChatService.get_messages(db_session, chat.id)
        assert len(messages) == 2
        assert messages[0].role == "user"
        assert messages[1].role == "assistant"

    def test_get_user_chats(self, db_session):
        """Test getting user's chats."""
        user_id = uuid4()

        # Create multiple chats
        ChatService.create_chat(db_session, user_id, "Chat 1", "private")
        ChatService.create_chat(db_session, user_id, "Chat 2", "private")

        chats = ChatService.get_user_chats(db_session, user_id)
        assert len(chats) == 2

    def test_update_chat_context(self, db_session):
        """Test updating chat context."""
        user_id = uuid4()
        chat = ChatService.create_chat(db_session, user_id, "Test Chat", "private")

        context = {"tokens": 100, "model": "phi3:mini"}
        updated = ChatService.update_chat_context(db_session, chat.id, context)

        assert updated is True
        retrieved = ChatService.get_chat(db_session, chat.id, user_id)
        assert retrieved.last_context == context

