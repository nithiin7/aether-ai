"""LLM service for Ollama integration with LangChain."""
from typing import Any, AsyncIterator, Dict, List, Optional

from langchain_community.llms import Ollama
from langchain_core.callbacks import AsyncCallbackHandler, CallbackManagerForLLMRun
from langchain_core.language_models import BaseLLM
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain_core.outputs import GenerationChunk

from src.config.settings import settings


class StreamingCallbackHandler(AsyncCallbackHandler):
    """Callback handler for streaming responses."""

    def __init__(self):
        """Initialize callback handler."""
        self.tokens = []

    async def on_llm_new_token(
        self, token: str, *, run_id, parent_run_id=None, **kwargs: Any
    ) -> None:
        """Handle new token from LLM."""
        self.tokens.append(token)


class OllamaModelRegistry:
    """Registry for managing Ollama models."""

    AVAILABLE_MODELS = {
        "phi3:mini": {
            "id": "phi3:mini",
            "name": "Phi-3 Mini",
            "description": "Fast 3.8B model for testing and quick responses",
            "size": "3.8B",
            "capabilities": ["chat", "text"],
        },
        "llama3.2:3b": {
            "id": "llama3.2:3b",
            "name": "Llama 3.2 3B",
            "description": "Efficient 3B model with good performance",
            "size": "3B",
            "capabilities": ["chat", "text"],
        },
        "llama3.2:11b-vision": {
            "id": "llama3.2:11b-vision",
            "name": "Llama 3.2 Vision 11B",
            "description": "Multimodal model with vision and text capabilities",
            "size": "11B",
            "capabilities": ["chat", "text", "vision"],
        },
        "qwen2.5:7b": {
            "id": "qwen2.5:7b",
            "name": "Qwen 2.5 7B",
            "description": "Multilingual model with strong reasoning",
            "size": "7B",
            "capabilities": ["chat", "text", "multilingual"],
        },
        "mixtral:8x7b": {
            "id": "mixtral:8x7b",
            "name": "Mixtral 8x7B",
            "description": "Powerful mixture-of-experts model",
            "size": "47B",
            "capabilities": ["chat", "text", "reasoning"],
        },
    }

    @classmethod
    def get_model_info(cls, model_id: str) -> Optional[Dict[str, Any]]:
        """Get model information by ID."""
        return cls.AVAILABLE_MODELS.get(model_id)

    @classmethod
    def list_models(cls) -> List[Dict[str, Any]]:
        """List all available models."""
        return list(cls.AVAILABLE_MODELS.values())

    @classmethod
    def is_valid_model(cls, model_id: str) -> bool:
        """Check if model ID is valid."""
        return model_id in cls.AVAILABLE_MODELS


class LLMService:
    """Service for managing LLM interactions."""

    def __init__(self, model_id: Optional[str] = None):
        """
        Initialize LLM service.

        Args:
            model_id: Ollama model ID to use
        """
        self.model_id = model_id or settings.OLLAMA_DEFAULT_MODEL
        self.ollama_host = settings.OLLAMA_HOST
        self._llm = None

    def _get_llm(self) -> Ollama:
        """Get or create Ollama LLM instance."""
        if self._llm is None:
            self._llm = Ollama(
                base_url=self.ollama_host,
                model=self.model_id,
                temperature=0.7,
            )
        return self._llm

    def _convert_messages_to_prompt(
        self, messages: List[Dict[str, Any]], system_prompt: Optional[str] = None
    ) -> str:
        """
        Convert message history to a prompt string.

        Args:
            messages: List of message dictionaries
            system_prompt: Optional system prompt

        Returns:
            Formatted prompt string
        """
        prompt_parts = []

        if system_prompt:
            prompt_parts.append(f"System: {system_prompt}\n")

        for msg in messages:
            role = msg.get("role", "user")
            content = ""

            # Handle parts-based content
            if "parts" in msg:
                for part in msg["parts"]:
                    if part.get("type") == "text":
                        content += part.get("text", "")
            # Handle direct content
            elif "content" in msg:
                content = msg["content"]

            if content:
                if role == "user":
                    prompt_parts.append(f"User: {content}")
                elif role == "assistant":
                    prompt_parts.append(f"Assistant: {content}")

        prompt_parts.append("Assistant:")
        return "\n\n".join(prompt_parts)

    async def stream_chat(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """
        Stream chat responses.

        Args:
            messages: List of message dictionaries
            system_prompt: Optional system prompt
            temperature: Temperature for generation

        Yields:
            Token strings as they are generated
        """
        llm = Ollama(
            base_url=self.ollama_host,
            model=self.model_id,
            temperature=temperature,
        )

        prompt = self._convert_messages_to_prompt(messages, system_prompt)

        # Stream tokens
        for chunk in llm.stream(prompt):
            if chunk:
                yield chunk

    def generate_chat(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
    ) -> str:
        """
        Generate chat response (non-streaming).

        Args:
            messages: List of message dictionaries
            system_prompt: Optional system prompt
            temperature: Temperature for generation

        Returns:
            Generated response text
        """
        llm = Ollama(
            base_url=self.ollama_host,
            model=self.model_id,
            temperature=temperature,
        )

        prompt = self._convert_messages_to_prompt(messages, system_prompt)
        response = llm.invoke(prompt)

        return response

    def generate_title(self, user_message: str) -> str:
        """
        Generate a title for a chat based on the first user message.

        Args:
            user_message: The user's first message

        Returns:
            Generated title
        """
        llm = Ollama(
            base_url=self.ollama_host,
            model=self.model_id,
            temperature=0.5,
        )

        prompt = f"""Generate a short, concise title (max 6 words) for a conversation that starts with:

User: {user_message}

Title:"""

        response = llm.invoke(prompt)
        # Clean up the response
        title = response.strip().strip('"').strip("'")
        # Limit to 60 characters
        if len(title) > 60:
            title = title[:57] + "..."

        return title

    @staticmethod
    def list_available_models() -> List[Dict[str, Any]]:
        """
        List all available models.

        Returns:
            List of model information dictionaries
        """
        return OllamaModelRegistry.list_models()

    @staticmethod
    def get_model_info(model_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific model.

        Args:
            model_id: Model ID

        Returns:
            Model information dictionary or None
        """
        return OllamaModelRegistry.get_model_info(model_id)

