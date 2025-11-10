"""Chat blueprint for handling chat endpoints."""
import asyncio
from uuid import UUID, uuid4

from flask import Blueprint, Response, jsonify, request, stream_with_context
from sqlalchemy.orm import Session

from src.config.database import SessionLocal
from src.services.chat_service import ChatService
from src.services.llm_service import LLMService
from src.services.streaming_service import SSEService
from src.services.tools.document_tools import (
    create_document_tool,
    request_suggestions_tool,
    update_document_tool,
)
from src.services.tools.weather_tool import get_weather
from src.utils.auth import get_user_id_from_request, require_auth
from src.utils.errors import BadRequestError, ForbiddenError, NotFoundError

chat_bp = Blueprint("chat", __name__, url_prefix="/api/chat")


async def stream_chat_response(
    db: Session,
    user_id: UUID,
    chat_id: UUID,
    messages: list,
    model_id: str,
    system_prompt: str = None,
):
    """
    Stream chat response using LLM.

    Args:
        db: Database session
        user_id: User ID
        chat_id: Chat ID
        messages: Message history
        model_id: Model to use
        system_prompt: Optional system prompt

    Yields:
        SSE-formatted response chunks
    """
    llm_service = LLMService(model_id)
    assistant_message_id = str(uuid4())
    full_response = ""

    try:
        # Send message start event
        yield SSEService.format_sse(
            {"type": "message-start", "id": assistant_message_id, "chat_id": str(chat_id)},
            event="message",
        )

        # Stream tokens
        async for token in llm_service.stream_chat(
            messages=messages, system_prompt=system_prompt
        ):
            full_response += token
            yield SSEService.format_sse({"type": "text-delta", "content": token}, event="message")

        # Save assistant message
        ChatService.add_message(
            db,
            chat_id,
            role="assistant",
            parts=[{"type": "text", "text": full_response}],
            attachments=[],
        )

        # Send message finish event
        yield SSEService.format_sse(
            {"type": "message-finish", "id": assistant_message_id}, event="message"
        )

    except Exception as e:
        yield SSEService.stream_error(str(e))
    finally:
        db.close()


def stream_chat_response_sync(
    db: Session,
    user_id: UUID,
    chat_id: UUID,
    messages: list,
    model_id: str,
    system_prompt: str = None,
):
    """Synchronous wrapper for async streaming function."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        async_gen = stream_chat_response(db, user_id, chat_id, messages, model_id, system_prompt)
        while True:
            try:
                chunk = loop.run_until_complete(async_gen.__anext__())
                yield chunk
            except StopAsyncIteration:
                break
    finally:
        loop.close()

@chat_bp.route("", methods=["POST"])
@require_auth
def create_or_continue_chat():
    """Create or continue a chat conversation with streaming response."""
    user_id = get_user_id_from_request()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    if not data:
        return jsonify({"error": "Invalid request body"}), 400

    chat_id = data.get("chat_id")
    message = data.get("message")
    model_id = data.get("model_id", "phi3:mini")
    system_prompt = data.get("system_prompt")

    if not message or not message.get("parts"):
        return jsonify({"error": "Message is required"}), 400

    db = SessionLocal()

    try:
        # Get or create chat
        chat = None
        if chat_id:
            try:
                chat_uuid = UUID(chat_id)
                chat = ChatService.get_chat(db, chat_uuid, user_id)
            except ValueError:
                # Invalid UUID format, create new chat
                chat = None
        
        # If no chat_id provided or chat not found, create new chat
        if not chat:
            llm_service = LLMService(model_id)
            user_text = ""
            for part in message.get("parts", []):
                if part.get("type") == "text":
                    user_text += part.get("text", "")

            title = llm_service.generate_title(user_text)
            chat = ChatService.create_chat(
                db, user_id, title, visibility=data.get("visibility", "private")
            )
            chat_uuid = chat.id
        else:
            chat_uuid = chat.id

        # Save user message
        ChatService.add_message(
            db,
            chat_uuid,
            role=message.get("role", "user"),
            parts=message.get("parts"),
            attachments=message.get("attachments", []),
        )

        # Get message history
        messages = ChatService.get_messages(db, chat_uuid)
        message_history = [
            {"role": msg.role, "parts": msg.parts, "attachments": msg.attachments}
            for msg in messages
        ]

        # Stream response
        return Response(
            stream_with_context(
                stream_chat_response_sync(
                    db, user_id, chat_uuid, message_history, model_id, system_prompt
                )
            ),
            mimetype="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
                "Connection": "keep-alive",
            },
        )

    except Exception as e:
        db.close()
        return jsonify({"error": str(e)}), 500


@chat_bp.route("", methods=["DELETE"])
@require_auth
def delete_chat():
    """
    Delete a chat by ID.

    Query params:
        id: Chat ID
    """
    user_id = get_user_id_from_request()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    chat_id = request.args.get("id")
    if not chat_id:
        return jsonify({"error": "Chat ID is required"}), 400

    db = SessionLocal()

    try:
        chat_uuid = UUID(chat_id)
        deleted = ChatService.delete_chat(db, chat_uuid, user_id)

        if deleted:
            return jsonify({"success": True, "id": chat_id}), 200
        else:
            return jsonify({"error": "Chat not found"}), 404

    except ValueError:
        return jsonify({"error": "Invalid chat ID format"}), 400
    finally:
        db.close()


@chat_bp.route("/<chat_id>/messages", methods=["GET"])
@require_auth
def get_chat_messages(chat_id: str):
    """
    Get messages for a chat.

    Path params:
        chat_id: Chat ID
    """
    user_id = get_user_id_from_request()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    db = SessionLocal()

    try:
        chat_uuid = UUID(chat_id)
        # Verify ownership
        chat = ChatService.get_chat(db, chat_uuid, user_id)
        if not chat:
            return jsonify({"error": "Chat not found"}), 404

        messages = ChatService.get_messages(db, chat_uuid)
        return jsonify({"messages": [msg.to_dict() for msg in messages]}), 200

    except ValueError:
        return jsonify({"error": "Invalid chat ID format"}), 400
    finally:
        db.close()

