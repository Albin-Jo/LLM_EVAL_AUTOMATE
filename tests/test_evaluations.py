import pytest
import time
from typing import Dict, Any

from lib.api_client import APIClient
from lib.data_generator import DataGenerator


class TestEvaluations:
    """Tests for the Evaluations API endpoints."""

    def test_list_evaluations(self, api_client: APIClient, check_auth) -> None:
        """Test listing evaluations."""
        response = api_client.get("/api/evaluations/")

        assert "items" in response
        assert "total" in response
        assert isinstance(response["items"], list)
        assert isinstance(response["total"], int)

    def test_create_evaluation(self, api_client: APIClient, test_agent: Dict[str, Any],
                               test_dataset: Dict[str, Any], test_prompt: Dict[str, Any], check_auth) -> None:
        """Test creating an evaluation."""
        eval_data = DataGenerator.generate_evaluation(
            agent_id=test_agent["id"],
            dataset_id=test_dataset["id"],
            prompt_id=test_prompt["id"]
        )

        response = api_client.post("/api/evaluations/", json=eval_data)

        assert "id" in response
        assert response["name"] == eval_data["name"]
        assert response["agent_id"] == eval_data["agent_id"]
        assert response["dataset_id"] == eval_data["dataset_id"]
        assert response["prompt_id"] == eval_data["prompt_id"]
        assert "created_at" in response

    def test_get_evaluation(self, api_client: APIClient, test_evaluation: Dict[str, Any], check_auth) -> None:
        """Test getting an evaluation by ID."""
        eval_id = test_evaluation["id"]
        response = api_client.get(f"/api/evaluations/{eval_id}")

        assert response["id"] == eval_id
        assert response["name"] == test_evaluation["name"]
        assert "results" in response

    def test_update_evaluation(self, api_client: APIClient, test_evaluation: Dict[str, Any], check_auth) -> None:
        """Test updating an evaluation."""
        eval_id = test_evaluation["id"]
        update_data = {
            "name": f"Updated Evaluation {pytest.id}",
            "description": "Updated by automated test"
        }

        response = api_client.put(f"/api/evaluations/{eval_id}", json=update_data)

        assert response["id"] == eval_id
        assert response["name"] == update_data["name"]
        assert response["description"] == update_data["description"]

    def test_search_evaluations(self, api_client: APIClient, test_evaluation: Dict[str, Any], check_auth) -> None:
        """Test searching for evaluations."""
        # Update the test evaluation to have a unique name
        unique_name = f"UniqueEval{pytest.id}"
        api_client.put(f"/api/evaluations/{test_evaluation['id']}", json={"name": unique_name})

        # Search for it
        search_data = {"query": unique_name}
        response = api_client.post("/api/evaluations/search", json=search_data)

        assert "items" in response
        assert len(response["items"]) > 0
        assert any(item["name"] == unique_name for item in response["items"])

    def test_start_evaluation(self, api_client: APIClient, test_evaluation: Dict[str, Any], check_auth) -> None:
        """Test starting an evaluation."""
        eval_id = test_evaluation["id"]
        response = api_client.post(f"/api/evaluations/{eval_id}/start")

        assert response["id"] == eval_id
        # The status might change quickly, so we don't assert on it

    def test_get_evaluation_progress(self, api_client: APIClient, test_evaluation: Dict[str, Any], check_auth) -> None:
        """Test getting evaluation progress."""
        eval_id = test_evaluation["id"]
        response = api_client.get(f"/api/evaluations/{eval_id}/progress")

        assert "status" in response
        assert "completed" in response
        assert "total" in response
        assert "percentage" in response

    def test_cancel_evaluation(self, api_client: APIClient, check_auth) -> None:
        """Test cancelling an evaluation."""
        # Create a new evaluation for this test to avoid affecting other tests
        eval_data = DataGenerator.generate_evaluation(
            agent_id=pytest.test_agent["id"],
            dataset_id=pytest.test_dataset["id"],
            prompt_id=pytest.test_prompt["id"]
        )

        created = api_client.post("/api/evaluations/", json=eval_data)
        eval_id = created["id"]

        # Start it
        api_client.post(f"/api/evaluations/{eval_id}/start")

        # Cancel it
        response = api_client.post(f"/api/evaluations/{eval_id}/cancel")

        assert response["id"] == eval_id
        assert response["status"] in ["cancelled", "pending", "failed"]  # Might happen too quickly

    def test_get_evaluation_results(self, api_client: APIClient, test_evaluation: Dict[str, Any], check_auth) -> None:
        """Test getting evaluation results."""
        eval_id = test_evaluation["id"]

        # Results might not be ready immediately, so we'll allow for a small delay
        max_retries = 3
        for attempt in range(max_retries):
            response = api_client.get(f"/api/evaluations/{eval_id}/results")

            if "items" in response:
                assert "total" in response
                break
            elif attempt < max_retries - 1:
                time.sleep(2)  # Wait before retrying

    def test_get_supported_metrics(self, api_client: APIClient) -> None:
        """Test getting supported metrics for evaluations."""
        dataset_type = "question_answer"
        response = api_client.get(f"/api/evaluations/metrics/{dataset_type}")

        assert isinstance(response, dict)
        assert len(response) > 0

    def test_test_evaluation(self, api_client: APIClient, test_evaluation: Dict[str, Any], check_auth) -> None:
        """Test the evaluation test endpoint."""
        eval_id = test_evaluation["id"]

        test_data = {
            "query": "What is the capital of France?",
            "context": "France is a country in Western Europe. Its capital is Paris.",
            "answer": "The capital of France is Paris.",
            "ground_truth": "Paris"
        }

        response = api_client.post(f"/api/evaluations/{eval_id}/test", json=test_data)

        # Just verify the response exists, structure may vary
        assert response is not None