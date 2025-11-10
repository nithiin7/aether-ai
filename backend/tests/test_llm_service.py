"""Tests for LLM service."""
import pytest
from src.services.llm_service import LLMService, OllamaModelRegistry


class TestOllamaModelRegistry:
    """Test Ollama model registry."""

    def test_list_models(self):
        """Test listing available models."""
        models = OllamaModelRegistry.list_models()
        assert isinstance(models, list)
        assert len(models) > 0
        assert all("id" in model for model in models)
        assert all("name" in model for model in models)

    def test_get_model_info(self):
        """Test getting model information."""
        model_info = OllamaModelRegistry.get_model_info("phi3:mini")
        assert model_info is not None
        assert model_info["id"] == "phi3:mini"
        assert "capabilities" in model_info

    def test_get_invalid_model(self):
        """Test getting info for invalid model."""
        model_info = OllamaModelRegistry.get_model_info("invalid-model")
        assert model_info is None

    def test_is_valid_model(self):
        """Test model validation."""
        assert OllamaModelRegistry.is_valid_model("phi3:mini") is True
        assert OllamaModelRegistry.is_valid_model("invalid-model") is False


class TestLLMService:
    """Test LLM service."""

    def test_initialization(self):
        """Test LLM service initialization."""
        service = LLMService("phi3:mini")
        assert service.model_id == "phi3:mini"
        assert service._llm is None

    def test_convert_messages_to_prompt(self):
        """Test message conversion to prompt."""
        service = LLMService("phi3:mini")
        messages = [
            {"role": "user", "parts": [{"type": "text", "text": "Hello"}]},
            {"role": "assistant", "parts": [{"type": "text", "text": "Hi there!"}]},
        ]
        prompt = service._convert_messages_to_prompt(messages)
        assert "User: Hello" in prompt
        assert "Assistant: Hi there!" in prompt

    def test_convert_messages_with_system_prompt(self):
        """Test message conversion with system prompt."""
        service = LLMService("phi3:mini")
        messages = [{"role": "user", "parts": [{"type": "text", "text": "Hello"}]}]
        prompt = service._convert_messages_to_prompt(messages, system_prompt="You are helpful")
        assert "System: You are helpful" in prompt
        assert "User: Hello" in prompt

    def test_list_available_models(self):
        """Test listing available models."""
        models = LLMService.list_available_models()
        assert isinstance(models, list)
        assert len(models) > 0

    def test_get_model_info(self):
        """Test getting model info."""
        info = LLMService.get_model_info("phi3:mini")
        assert info is not None
        assert info["id"] == "phi3:mini"

