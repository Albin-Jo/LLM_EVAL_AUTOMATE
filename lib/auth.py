import logging
from typing import Dict, Any, Optional
from lib.api_client import APIClient

logger = logging.getLogger(__name__)


class Auth:
    """Handle authentication and token management."""

    def __init__(self, api_client: APIClient):
        self.api_client = api_client

    def check_status(self) -> Dict[str, Any]:
        """Check authentication status."""
        return self.api_client.get("/api/auth/status")

    def get_current_user(self) -> Dict[str, Any]:
        """Get information about the authenticated user."""
        return self.api_client.get("/api/auth/me")

    def logout(self) -> Dict[str, Any]:
        """Logout the current user."""
        return self.api_client.post("/api/auth/logout")

    def validate_token(self) -> bool:
        """Validate the current token by checking auth status."""
        try:
            status = self.check_status()
            return status.get("authenticated", False)
        except Exception as e:
            logger.error(f"Error validating token: {e}")
            return False