import pytest
from typing import Dict, Any

from lib.api_client import APIClient
from lib.data_generator import DataGenerator


class TestPrompts:
    """Tests for the Prompts API endpoints."""

    def test_list_prompts(self, api_client: APIClient) -> None:
        """Test listing prompts."""
        response = api_client.get("/api/prompts/")

        assert "items" in response
        assert "total" in response
        assert isinstance(response["items"], list)
        assert isinstance(response["total"], int)

    def test_create_prompt(self, api_client: APIClient) -> None:
        """Test creating a prompt."""
        prompt_data = DataGenerator.generate_prompt()

        response = api_client.post("/api/prompts/", json=prompt_data)

        assert "id" in response
        assert response["name"] == prompt_data["name"]
        assert response["content"] == prompt_data["content"]
        assert "created_at" in response

        # Save for later tests
        pytest.created_prompt_id = response["id"]

    def test_get_prompt(self, api_client: APIClient) -> None:
        """Test getting a prompt by ID."""
        prompt_id = pytest.created_prompt_id  # From test_create_prompt

        response = api_client.get(f"/api/prompts/{prompt_id}")

        assert response["id"] == prompt_id
        assert "name" in response
        assert "content" in response

    def test_update_prompt(self, api_client: APIClient) -> None:
        """Test updating a prompt."""
        prompt_id = pytest.created_prompt_id  # From test_create_prompt

        update_data = {
            "name": f"Updated Prompt {pytest.id}",
            "description": "Updated by automated test",
            "content": "This is updated prompt content for testing."
        }

        response = api_client.put(f"/api/prompts/{prompt_id}", json=update_data)

        assert response["id"] == prompt_id
        assert response["name"] == update_data["name"]
        assert response["description"] == update_data["description"]
        assert response["content"] == update_data["content"]

    def test_delete_prompt(self, api_client: APIClient) -> None:
        """Test deleting a prompt."""
        # Create a new prompt to delete
        prompt_data = DataGenerator.generate_prompt()
        created = api_client.post("/api/prompts/", json=prompt_data)
        prompt_id = created["id"]

        # Delete it
        api_client.delete(f"/api/prompts/{prompt_id}")

        # Verify it's deleted
        with pytest.raises(Exception):
            api_client.get(f"/api/prompts/{prompt_id}")