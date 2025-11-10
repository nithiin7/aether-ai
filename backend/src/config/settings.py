"""Application settings and configuration."""
import os
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Flask Configuration
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    FLASK_ENV: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/aether_ai"

    # Ollama Configuration
    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_DEFAULT_MODEL: str = "phi3:mini"

    # API Configuration
    BACKEND_API_KEY: str = "shared-secret-between-frontend-and-backend"

    # Weather API (optional)
    WEATHER_API_KEY: str = ""

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001"

    # Logging
    LOG_LEVEL: str = "INFO"

    # Storage
    UPLOAD_FOLDER: str = "storage/uploads"
    MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024  # 16MB

    class Config:
        """Pydantic config."""

        env_file = ".env"
        case_sensitive = True

    def get_cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


# Global settings instance
settings = Settings()

