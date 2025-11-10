"""Authentication utilities for verifying Next.js session tokens."""
import jwt
from functools import wraps
from typing import Optional
from uuid import UUID

from flask import request, jsonify

from src.config.settings import settings


def extract_user_from_token(token: str) -> Optional[dict]:
    """
    Extract user information from JWT token.

    Args:
        token: JWT token string

    Returns:
        User information dictionary or None
    """
    try:
        # Decode JWT token (Next.js uses HS256 by default)
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_user_from_request() -> Optional[dict]:
    """
    Get user information from request.

    Checks multiple sources:
    1. Authorization header (Bearer token)
    2. x-user-id header (for development)
    3. Cookie (next-auth session)

    Returns:
        User information dictionary or None
    """
    # Check Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        user = extract_user_from_token(token)
        if user:
            return user

    # Check x-user-id header (for development/testing)
    user_id_header = request.headers.get("x-user-id")
    if user_id_header:
        try:
            return {"id": user_id_header, "email": "dev@example.com"}
        except ValueError:
            pass

    # Check cookies for next-auth session
    # Note: In production, you'll need to decode the next-auth session cookie
    # For now, we'll accept the user ID from headers
    
    return None


def verify_api_key() -> bool:
    """
    Verify API key from request headers.

    Returns:
        True if API key is valid
    """
    api_key = request.headers.get("X-API-Key")
    return api_key == settings.BACKEND_API_KEY


def require_auth(f):
    """
    Decorator to require authentication.

    Usage:
        @require_auth
        def my_route():
            user = get_user_from_request()
            ...
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_user_from_request()
        if not user:
            return jsonify({"error": "Unauthorized", "code": "unauthorized"}), 401
        return f(*args, **kwargs)

    return decorated_function


def require_api_key(f):
    """
    Decorator to require API key authentication.

    Usage:
        @require_api_key
        def my_route():
            ...
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not verify_api_key():
            return jsonify({"error": "Invalid API key", "code": "invalid_api_key"}), 403
        return f(*args, **kwargs)

    return decorated_function


def get_user_id_from_request() -> Optional[UUID]:
    """
    Get user ID from request as UUID.

    Returns:
        User UUID or None
    """
    user = get_user_from_request()
    if user and "id" in user:
        try:
            return UUID(user["id"])
        except (ValueError, TypeError):
            pass
    return None

