"""Suggestions blueprint for document suggestions."""
from uuid import UUID

from flask import Blueprint, jsonify, request

from src.config.database import SessionLocal
from src.services.document_service import DocumentService
from src.utils.auth import get_user_id_from_request, require_auth

suggestions_bp = Blueprint("suggestions", __name__, url_prefix="/api/suggestions")


@suggestions_bp.route("/<document_id>", methods=["GET"])
@require_auth
def get_document_suggestions(document_id: str):
    """
    Get suggestions for a document.

    Path params:
        document_id: Document ID

    Query params:
        include_resolved: Include resolved suggestions (default false)
    """
    user_id = get_user_id_from_request()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    include_resolved = request.args.get("include_resolved", "false").lower() == "true"

    db = SessionLocal()

    try:
        doc_uuid = UUID(document_id)

        # Verify document ownership
        document = DocumentService.get_document(db, doc_uuid, user_id)
        if not document:
            return jsonify({"error": "Document not found"}), 404

        suggestions = DocumentService.get_document_suggestions(db, doc_uuid, include_resolved)
        return jsonify({"suggestions": [sug.to_dict() for sug in suggestions]}), 200

    except ValueError:
        return jsonify({"error": "Invalid document ID format"}), 400
    finally:
        db.close()


@suggestions_bp.route("/<suggestion_id>/resolve", methods=["POST"])
@require_auth
def resolve_suggestion(suggestion_id: str):
    """
    Mark a suggestion as resolved.

    Path params:
        suggestion_id: Suggestion ID
    """
    user_id = get_user_id_from_request()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    db = SessionLocal()

    try:
        sug_uuid = UUID(suggestion_id)
        resolved = DocumentService.resolve_suggestion(db, sug_uuid)

        if resolved:
            return jsonify({"success": True, "id": suggestion_id}), 200
        else:
            return jsonify({"error": "Suggestion not found"}), 404

    except ValueError:
        return jsonify({"error": "Invalid suggestion ID format"}), 400
    finally:
        db.close()

