"""Main Flask application factory."""
import logging
from flask import Flask, jsonify
from flask_cors import CORS

from src.api.blueprints.chat import chat_bp
from src.api.blueprints.document import document_bp
from src.api.blueprints.health import health_bp
from src.api.blueprints.history import history_bp
from src.api.blueprints.suggestions import suggestions_bp
from src.config.database import db_session
from src.config.settings import settings
from src.utils.errors import APIError


def create_app():
    """
    Create and configure Flask application.

    Returns:
        Flask app instance
    """
    app = Flask(__name__)

    # Configuration
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config["MAX_CONTENT_LENGTH"] = settings.MAX_CONTENT_LENGTH

    # CORS configuration
    CORS(
        app,
        origins=settings.get_cors_origins(),
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization", "X-API-Key", "X-User-Id"],
    )

    # Logging
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Register blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(document_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(suggestions_bp)

    # Error handlers
    @app.errorhandler(APIError)
    def handle_api_error(error):
        """Handle API errors."""
        return jsonify(error.to_dict()), error.status_code

    @app.errorhandler(404)
    def handle_not_found(error):
        """Handle 404 errors."""
        return jsonify({"error": "Not found", "code": "not_found"}), 404

    @app.errorhandler(500)
    def handle_internal_error(error):
        """Handle 500 errors."""
        app.logger.error(f"Internal error: {error}")
        return jsonify({"error": "Internal server error", "code": "internal_error"}), 500

    # Database session cleanup
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        """Remove database session at the end of request."""
        db_session.remove()

    # Root endpoint
    @app.route("/")
    def root():
        """Root endpoint."""
        return jsonify(
            {
                "service": "Aether AI Backend",
                "version": "0.1.0",
                "status": "running",
                "endpoints": {
                    "health": "/api/health",
                    "models": "/api/health/models",
                    "chat": "/api/chat",
                    "documents": "/api/document",
                    "history": "/api/history",
                    "suggestions": "/api/suggestions",
                },
            }
        )

    return app


# For development
if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5001, debug=settings.DEBUG)

