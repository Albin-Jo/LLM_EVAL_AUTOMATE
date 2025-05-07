import pytest
import uuid
from typing import Dict, Any

from lib.api_client import APIClient
from lib.data_generator import DataGenerator


class TestAgents:
    """Tests for the Agents API endpoints."""

    @pytest.fixture
    def agent_data(self) -> Dict[str, Any]:
        """Generate test data for an agent."""
        return DataGenerator.generate_agent()

    def test_create_agent(self, api_client: APIClient, agent_data: Dict[str, Any]) -> None:
        """Test creating an agent."""
        response = api_client.post("/api/agents/", json=agent_data)

        assert "id" in response
        assert response["name"] == agent_data["name"]
        assert response["domain"] == agent_data["domain"]
        assert "created_at" in response

    def test_list_agents(self, api_client: APIClient) -> None:
        """Test listing agents."""
        response = api_client.get("/api/agents/")

        assert "items" in response
        assert "total" in response
        assert isinstance(response["items"], list)
        assert isinstance(response["total"], int)

    def test_get_agent(self, api_client: APIClient, agent_data: Dict[str, Any]) -> None:
        """Test getting an agent by ID."""
        # First create an agent
        created = api_client.post("/api/agents/", json=agent_data)
        agent_id = created["id"]

        # Then retrieve it
        response = api_client.get(f"/api/agents/{agent_id}")

        assert response["id"] == agent_id
        assert response["name"] == agent_data["name"]

    def test_update_agent(self, api_client: APIClient, agent_data: Dict[str, Any]) -> None:
        """Test updating an agent."""
        # First create an agent
        created = api_client.post("/api/agents/", json=agent_data)
        agent_id = created["id"]

        # Update data
        update_data = {"name": "Updated Agent Name"}

        # Then update it
        response = api_client.put(f"/api/agents/{agent_id}", json=update_data)

        assert response["id"] == agent_id
        assert response["name"] == update_data["name"]
        # Other fields should remain unchanged
        assert response["domain"] == agent_data["domain"]

    def test_delete_agent(self, api_client: APIClient, agent_data: Dict[str, Any]) -> None:
        """Test deleting an agent."""
        # First create an agent
        created = api_client.post("/api/agents/", json=agent_data)
        agent_id = created["id"]

        # Then delete it
        api_client.delete(f"/api/agents/{agent_id}")

        # Verify it's gone by trying to retrieve it (should raise an exception)
        with pytest.raises(Exception):
            api_client.get(f"/api/agents/{agent_id}")

    def test_search_agents(self, api_client: APIClient, agent_data: Dict[str, Any]) -> None:
        """Test searching for agents."""
        # First create an agent with a unique name
        unique_name = f"Unique{uuid.uuid4().hex[:8]}"
        agent_data["name"] = unique_name
        api_client.post("/api/agents/", json=agent_data)

        # Search for it
        search_data = {"query": unique_name}
        response = api_client.post("/api/agents/search", json=search_data)

        assert "items" in response
        assert len(response["items"]) > 0
        assert any(item["name"] == unique_name for item in response["items"])

    def test_agent_test_endpoint(self, api_client: APIClient, agent_data: Dict[str, Any]) -> None:
        """Test the agent test endpoint."""
        # First create an agent
        created = api_client.post("/api/agents/", json=agent_data)
        agent_id = created["id"]

        # Test data
        test_input = {"query": "What is the capital of France?"}

        # Test the agent
        response = api_client.post(f"/api/agents/{agent_id}/test", json=test_input)

        # The response structure will depend on the agent implementation
        # Just check that we get a response without an error
        assert response is not None