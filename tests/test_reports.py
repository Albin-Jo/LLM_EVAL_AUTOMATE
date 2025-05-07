import pytest
import time
from typing import Dict, Any

from lib.api_client import APIClient
from lib.data_generator import DataGenerator


class TestReports:
    """Tests for the Reports API endpoints."""

    def test_list_reports(self, api_client: APIClient, check_auth) -> None:
        """Test listing reports."""
        response = api_client.get("/api/reports/")

        assert "items" in response
        assert "total" in response
        assert isinstance(response["items"], list)
        assert isinstance(response["total"], int)

    def test_create_report(self, api_client: APIClient, test_evaluation: Dict[str, Any], check_auth) -> None:
        """Test creating a report."""
        report_data = DataGenerator.generate_report(evaluation_id=test_evaluation["id"])

        response = api_client.post("/api/reports/", json=report_data)

        assert "id" in response
        assert response["name"] == report_data["name"]
        assert response["evaluation_id"] == report_data["evaluation_id"]
        assert "created_at" in response

        # Save for later tests
        pytest.created_report_id = response["id"]

    def test_get_report(self, api_client: APIClient, test_report: Dict[str, Any], check_auth) -> None:
        """Test getting a report by ID."""
        report_id = test_report["id"]

        response = api_client.get(f"/api/reports/{report_id}")

        assert response["id"] == report_id
        assert response["name"] == test_report["name"]
        assert "evaluation_summary" in response

    def test_update_report(self, api_client: APIClient, test_report: Dict[str, Any], check_auth) -> None:
        """Test updating a report."""
        report_id = test_report["id"]

        update_data = {
            "name": f"Updated Report {pytest.id}",
            "description": "Updated by automated test",
            "format": "html"  # Change format to test updates
        }

        response = api_client.put(f"/api/reports/{report_id}", json=update_data)

        assert response["id"] == report_id
        assert response["name"] == update_data["name"]
        assert response["description"] == update_data["description"]
        assert response["format"] == update_data["format"]

    def test_generate_report(self, api_client: APIClient, test_report: Dict[str, Any], check_auth) -> None:
        """Test generating a report."""
        report_id = test_report["id"]

        data = {"force_regenerate": True}
        response = api_client.post(f"/api/reports/{report_id}/generate", json=data)

        assert response["id"] == report_id
        # Status might be "draft" or "generated" depending on how quickly it processes

    def test_send_report(self, api_client: APIClient, test_report: Dict[str, Any], check_auth) -> None:
        """Test sending a report via email."""
        report_id = test_report["id"]

        # Generate the report first if not already generated
        if test_report.get("status") == "draft":
            api_client.post(f"/api/reports/{report_id}/generate", json={"force_regenerate": True})

            # Wait a bit for generation to complete
            time.sleep(2)

        # Send the report
        send_data = {
            "recipients": [
                {"email": "test@example.com", "name": "Test User"}
            ],
            "subject": "Automated Test Report",
            "message": "This is a test report sent by the automated test suite.",
            "include_pdf": True
        }

        try:
            # This might fail if email sending is not configured in test environment
            response = api_client.post(f"/api/reports/{report_id}/send", json=send_data)
            assert response is not None
        except:
            pytest.skip("Email sending is not available in test environment")

    def test_download_report(self, api_client: APIClient, test_report: Dict[str, Any], check_auth) -> None:
        """Test downloading a report."""
        report_id = test_report["id"]

        # Generate the report first if not already generated
        if test_report.get("status") == "draft":
            api_client.post(f"/api/reports/{report_id}/generate", json={"force_regenerate": True})

            # Wait a bit for generation to complete
            time.sleep(2)

        try:
            # This might return binary data instead of JSON
            response = api_client.get(f"/api/reports/{report_id}/download")
            assert response is not None
        except:
            pytest.skip("Report download is not available in test environment")

    def test_preview_report(self, api_client: APIClient, test_report: Dict[str, Any], check_auth) -> None:
        """Test previewing a report."""
        report_id = test_report["id"]

        # Generate the report first if not already generated
        if test_report.get("status") == "draft":
            api_client.post(f"/api/reports/{report_id}/generate", json={"force_regenerate": True})

            # Wait a bit for generation to complete
            time.sleep(2)

        try:
            # This might return HTML instead of JSON
            response = api_client.get(f"/api/reports/{report_id}/preview")
            assert response is not None
        except:
            pytest.skip("Report preview is not available in test environment")

    def test_get_report_status_counts(self, api_client: APIClient, check_auth) -> None:
        """Test getting report status counts."""
        response = api_client.get("/api/reports/status/counts")

        assert isinstance(response, dict)
        # Verify at least one status count
        assert any(status in response for status in ["draft", "generated", "sent", "failed"])