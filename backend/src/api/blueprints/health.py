"""Health check blueprint."""
from flask import Blueprint, jsonify

from src.config.settings import settings

health_bp = Blueprint("health", __name__, url_prefix="/api/health")


@health_bp.route("", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify(
        {
            "status": "healthy",
            "service": "aether-ai-backend",
            "version": "0.1.0",
            "ollama_host": settings.OLLAMA_HOST,
        }
    )


@health_bp.route("/models", methods=["GET"])
def list_models():
    """List available models."""
    from src.services.llm_service import LLMService

    models = LLMService.list_available_models()
    return jsonify({"models": models})

