import pytest
import tempfile
import os
from typing import Dict, Any

from lib.api_client import APIClient
from lib.data_generator import DataGenerator


class TestDatasets:
    """Tests for the Datasets API endpoints."""

    def test_list_datasets(self, api_client: APIClient, check_auth) -> None:
        """Test listing datasets."""
        response = api_client.get("/api/datasets/")

        assert "items" in response
        assert "total" in response
        assert isinstance(response["items"], list)
        assert isinstance(response["total"], int)

    def test_create_and_get_dataset(self, api_client: APIClient, check_auth) -> None:
        """Test creating and then retrieving a dataset."""
        # Generate CSV content
        csv_content = DataGenerator.generate_csv_content(rows=3, dataset_type="question_answer")

        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp_file:
            temp_file.write(csv_content.encode('utf-8'))
            temp_path = temp_file.name

        try:
            # Prepare multipart form data
            dataset_name = f"Test Dataset {pytest.id}"
            files = {
                'file': ('test_data.csv', open(temp_path, 'rb'), 'text/csv')
            }
            data = {
                'name': dataset_name,
                'description': "Dataset created by automated test",
                'type': "question_answer",
                'is_public': "true"
            }

            # Create dataset
            created = api_client.post("/api/datasets/", data=data, files=files)

            assert "id" in created
            assert created["name"] == dataset_name
            assert created["type"] == "question_answer"

            # Get the created dataset
            dataset_id = created["id"]
            retrieved = api_client.get(f"/api/datasets/{dataset_id}")

            assert retrieved["id"] == dataset_id
            assert retrieved["name"] == dataset_name

        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_update_dataset(self, api_client: APIClient, test_dataset: Dict[str, Any], check_auth) -> None:
        """Test updating a dataset."""
        dataset_id = test_dataset["id"]
        update_data = {
            "name": f"Updated Dataset {pytest.id}",
            "description": "Updated by automated test"
        }

        response = api_client.put(f"/api/datasets/{dataset_id}", json=update_data)

        assert response["id"] == dataset_id
        assert response["name"] == update_data["name"]
        assert response["description"] == update_data["description"]

    def test_delete_dataset(self, api_client: APIClient, check_auth) -> None:
        """Test deleting a dataset."""
        # First create a dataset to delete
        csv_content = DataGenerator.generate_csv_content(rows=2, dataset_type="context")

        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp_file:
            temp_file.write(csv_content.encode('utf-8'))
            temp_path = temp_file.name

        try:
            files = {
                'file': ('delete_test.csv', open(temp_path, 'rb'), 'text/csv')
            }
            data = {
                'name': f"Delete Test Dataset {pytest.id}",
                'description': "Dataset to be deleted",
                'type': "context",
                'is_public': "false"
            }

            created = api_client.post("/api/datasets/", data=data, files=files)
            dataset_id = created["id"]

            # Delete the dataset
            api_client.delete(f"/api/datasets/{dataset_id}")

            # Verify it's deleted (should raise an exception)
            with pytest.raises(Exception):
                api_client.get(f"/api/datasets/{dataset_id}")

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_get_dataset_schema(self, api_client: APIClient) -> None:
        """Test getting the schema for a dataset type."""
        dataset_type = "question_answer"
        response = api_client.get(f"/api/datasets/schema/{dataset_type}")

        assert "dataset_type" in response
        assert response["dataset_type"] == dataset_type
        assert "schema" in response
        assert "supported_metrics" in response

    def test_get_supported_metrics(self, api_client: APIClient) -> None:
        """Test getting supported metrics for a dataset type."""
        dataset_type = "question_answer"
        response = api_client.get(f"/api/datasets/metrics/{dataset_type}")

        assert dataset_type in response
        assert isinstance(response[dataset_type], list)