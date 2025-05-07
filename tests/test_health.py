import pytest
from lib.api_client import APIClient


class TestHealth:
    """Tests for the Health API endpoints."""

    def test_health_check(self, api_client: APIClient) -> None:
        """Test the health check endpoint."""
        response = api_client.get("/health")

        # Health endpoint typically returns a simple status object
        assert response is not None