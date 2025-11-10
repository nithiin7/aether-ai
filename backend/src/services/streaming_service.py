"""Service for SSE streaming."""
import json
from typing import AsyncIterator, Dict, Any


class SSEService:
    """Service for Server-Sent Events streaming."""

    @staticmethod
    def format_sse(data: Dict[str, Any], event: str = "message") -> str:
        """
        Format data as SSE message.

        Args:
            data: Data to send
            event: Event type

        Returns:
            Formatted SSE string
        """
        lines = [f"event: {event}", f"data: {json.dumps(data)}", ""]
        return "\n".join(lines) + "\n"

    @staticmethod
    async def stream_chat_response(
        tokens: AsyncIterator[str], message_id: str
    ) -> AsyncIterator[str]:
        """
        Stream chat response tokens as SSE events.

        Args:
            tokens: Async iterator of token strings
            message_id: ID of the message being generated

        Yields:
            SSE-formatted strings
        """
        # Send initial message start event
        yield SSEService.format_sse(
            {"type": "message-start", "id": message_id}, event="message"
        )

        # Stream tokens
        async for token in tokens:
            yield SSEService.format_sse(
                {"type": "text-delta", "content": token}, event="message"
            )

        # Send message finish event
        yield SSEService.format_sse(
            {"type": "message-finish", "id": message_id}, event="message"
        )

    @staticmethod
    def stream_error(error_message: str, error_code: str = "internal_error") -> str:
        """
        Format error as SSE message.

        Args:
            error_message: Error message
            error_code: Error code

        Returns:
            SSE-formatted error string
        """
        return SSEService.format_sse(
            {"type": "error", "error": error_message, "code": error_code}, event="error"
        )

    @staticmethod
    def stream_tool_call(tool_name: str, tool_input: Dict[str, Any]) -> str:
        """
        Format tool call as SSE message.

        Args:
            tool_name: Name of the tool being called
            tool_input: Input parameters for the tool

        Returns:
            SSE-formatted tool call string
        """
        return SSEService.format_sse(
            {"type": "tool-call", "tool": tool_name, "input": tool_input}, event="tool"
        )

    @staticmethod
    def stream_tool_result(tool_name: str, tool_output: Any) -> str:
        """
        Format tool result as SSE message.

        Args:
            tool_name: Name of the tool that was called
            tool_output: Output from the tool

        Returns:
            SSE-formatted tool result string
        """
        return SSEService.format_sse(
            {"type": "tool-result", "tool": tool_name, "output": tool_output}, event="tool"
        )

    @staticmethod
    def stream_data(data_type: str, data: Any) -> str:
        """
        Format custom data as SSE message.

        Args:
            data_type: Type of data
            data: Data payload

        Returns:
            SSE-formatted data string
        """
        return SSEService.format_sse(
            {"type": f"data-{data_type}", "data": data}, event="data"
        )

