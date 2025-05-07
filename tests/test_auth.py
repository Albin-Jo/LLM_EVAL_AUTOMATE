import pytest
from lib.api_client import APIClient
from lib.auth import Auth


class TestAuth:
    """Tests for the Authentication API endpoints."""

    def test_auth_status(self, api_client: APIClient) -> None:
        """Test checking authentication status."""
        response = api_client.get("/api/auth/status")

        assert "authenticated" in response
        assert isinstance(response["authenticated"], bool)

    def test_get_current_user(self, api_client: APIClient, check_auth) -> None:
        """Test getting current user information."""
        response = api_client.get("/api/auth/me")

        assert "sub" in response
        assert "username" in response
        assert "email" in response
        assert "name" in response
        assert "roles" in response

    def test_logout(self, api_client: APIClient, check_auth) -> None:
        """Test logging out."""
        # Note: This test just verifies the endpoint works
        # It doesn't actually invalidate the token on the server
        response = api_client.post("/api/auth/logout")

        # Expect 204 No Content which results in an empty dict
        assert response == {}