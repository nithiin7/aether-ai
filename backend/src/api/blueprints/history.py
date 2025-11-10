"""History blueprint for chat history endpoints."""
from flask import Blueprint, jsonify

from src.config.database import SessionLocal
from src.services.chat_service import ChatService
from src.utils.auth import get_user_id_from_request, require_auth

history_bp = Blueprint("history", __name__, url_prefix="/api/history")


@history_bp.route("", methods=["GET"])
@require_auth
def get_user_history():
    """
    Get user's chat history.

    Returns list of user's chats ordered by most recent.
    """
    user_id = get_user_id_from_request()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    db = SessionLocal()

    try:
        chats = ChatService.get_user_chats(db, user_id, limit=50)
        return jsonify({"chats": [chat.to_dict() for chat in chats]}), 200
    finally:
        db.close()

