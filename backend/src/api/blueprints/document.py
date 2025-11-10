"""Document blueprint for artifact handling."""
from uuid import UUID

from flask import Blueprint, jsonify, request

from src.config.database import SessionLocal
from src.services.document_service import DocumentService
from src.utils.auth import get_user_id_from_request, require_auth

document_bp = Blueprint("document", __name__, url_prefix="/api/document")


@document_bp.route("", methods=["POST"])
@require_auth
def create_document():
    """
    Create a new document/artifact.

    Request body:
        {
            "title": "Document title",
            "content": "Initial content",
            "kind": "text|code|image|sheet"
        }
    """
    user_id = get_user_id_from_request()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    if not data or not data.get("title"):
        return jsonify({"error": "Title is required"}), 400

    title = data.get("title")
    content = data.get("content", "")
    kind = data.get("kind", "text")

    valid_kinds = ["text", "code", "image", "sheet"]
    if kind not in valid_kinds:
        return jsonify({"error": f"Invalid kind. Must be one of: {', '.join(valid_kinds)}"}), 400

    db = SessionLocal()

    try:
        document = DocumentService.create_document(db, user_id, title, content, kind)
        return jsonify(document.to_dict()), 201
    finally:
        db.close()


@document_bp.route("/<document_id>", methods=["GET"])
@require_auth
def get_document(document_id: str):
    """
    Get a document by ID.

    Path params:
        document_id: Document ID
    """
    user_id = get_user_id_from_request()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    db = SessionLocal()

    try:
        doc_uuid = UUID(document_id)
        document = DocumentService.get_document(db, doc_uuid, user_id)

        if not document:
            return jsonify({"error": "Document not found"}), 404

        return jsonify(document.to_dict()), 200

    except ValueError:
        return jsonify({"error": "Invalid document ID format"}), 400
    finally:
        db.close()


@document_bp.route("/<document_id>", methods=["PUT"])
@require_auth
def update_document(document_id: str):
    """
    Update a document's content.

    Path params:
        document_id: Document ID

    Request body:
        {
            "content": "Updated content"
        }
    """
    user_id = get_user_id_from_request()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    if not data or "content" not in data:
        return jsonify({"error": "Content is required"}), 400

    db = SessionLocal()

    try:
        doc_uuid = UUID(document_id)
        document = DocumentService.update_document(db, doc_uuid, user_id, data["content"])

        if not document:
            return jsonify({"error": "Document not found"}), 404

        return jsonify(document.to_dict()), 200

    except ValueError:
        return jsonify({"error": "Invalid document ID format"}), 400
    finally:
        db.close()


@document_bp.route("/<document_id>", methods=["DELETE"])
@require_auth
def delete_document(document_id: str):
    """
    Delete a document.

    Path params:
        document_id: Document ID
    """
    user_id = get_user_id_from_request()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    db = SessionLocal()

    try:
        doc_uuid = UUID(document_id)
        deleted = DocumentService.delete_document(db, doc_uuid, user_id)

        if deleted:
            return jsonify({"success": True, "id": document_id}), 200
        else:
            return jsonify({"error": "Document not found"}), 404

    except ValueError:
        return jsonify({"error": "Invalid document ID format"}), 400
    finally:
        db.close()


@document_bp.route("", methods=["GET"])
@require_auth
def list_documents():
    """
    List user's documents.

    Query params:
        kind: Optional filter by document kind
        limit: Maximum number of documents (default 50)
    """
    user_id = get_user_id_from_request()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    kind = request.args.get("kind")
    limit = int(request.args.get("limit", 50))

    db = SessionLocal()

    try:
        documents = DocumentService.get_user_documents(db, user_id, kind, limit)
        return jsonify({"documents": [doc.to_dict() for doc in documents]}), 200
    finally:
        db.close()

