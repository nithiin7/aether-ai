"""Error handling utilities."""
from typing import Any, Dict, Optional


class APIError(Exception):
    """Base API error class."""

    def __init__(
        self,
        message: str,
        code: str = "internal_error",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize API error.

        Args:
            message: Error message
            code: Error code
            status_code: HTTP status code
            details: Additional error details
        """
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary."""
        error_dict = {"error": self.message, "code": self.code}
        if self.details:
            error_dict["details"] = self.details
        return error_dict


class BadRequestError(APIError):
    """Bad request error (400)."""

    def __init__(self, message: str = "Bad request", code: str = "bad_request", **kwargs):
        """Initialize bad request error."""
        super().__init__(message, code, 400, **kwargs)


class UnauthorizedError(APIError):
    """Unauthorized error (401)."""

    def __init__(self, message: str = "Unauthorized", code: str = "unauthorized", **kwargs):
        """Initialize unauthorized error."""
        super().__init__(message, code, 401, **kwargs)


class ForbiddenError(APIError):
    """Forbidden error (403)."""

    def __init__(self, message: str = "Forbidden", code: str = "forbidden", **kwargs):
        """Initialize forbidden error."""
        super().__init__(message, code, 403, **kwargs)


class NotFoundError(APIError):
    """Not found error (404)."""

    def __init__(self, message: str = "Not found", code: str = "not_found", **kwargs):
        """Initialize not found error."""
        super().__init__(message, code, 404, **kwargs)


class RateLimitError(APIError):
    """Rate limit error (429)."""

    def __init__(
        self, message: str = "Rate limit exceeded", code: str = "rate_limit", **kwargs
    ):
        """Initialize rate limit error."""
        super().__init__(message, code, 429, **kwargs)


class InternalServerError(APIError):
    """Internal server error (500)."""

    def __init__(
        self, message: str = "Internal server error", code: str = "internal_error", **kwargs
    ):
        """Initialize internal server error."""
        super().__init__(message, code, 500, **kwargs)

