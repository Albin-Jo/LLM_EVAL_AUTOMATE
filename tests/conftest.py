import pytest
import os
import json
import time
from typing import Dict, Any, Optional

from lib.api_client import APIClient
from lib.auth import Auth
from lib.data_generator import DataGenerator

# Load environment variables
API_BASE_URL = os.environ.get("LLM_API_BASE_URL", "http://localhost:8000")
API_TOKEN = os.environ.get("LLM_API_TOKEN")

# Flags for test execution
GENERATE_DATA = not os.environ.get("NO_GENERATE_DATA", False)


@pytest.fixture(scope="session")
def api_client() -> APIClient:
    """Create an API client for tests."""
    client = APIClient(base_url=API_BASE_URL, token=API_TOKEN)
    return client


@pytest.fixture(scope="session")
def auth_client(api_client: APIClient) -> Auth:
    """Create an Auth client for tests."""
    return Auth(api_client)


@pytest.fixture(scope="session")
def check_auth(auth_client: Auth) -> None:
    """Check if authentication is valid."""
    if not auth_client.validate_token():
        pytest.skip("Authentication token is invalid or not provided")


# Resource fixtures for tests that need them
@pytest.fixture(scope="session")
def test_agent(api_client: APIClient, check_auth) -> Dict[str, Any]:
    """Create a test agent for use in other tests."""
    if not GENERATE_DATA:
        pytest.skip("Data generation is disabled")

    agent_data = DataGenerator.generate_agent()
    response = api_client.post("/api/agents/", json=agent_data)
    return response


@pytest.fixture(scope="session")
def test_prompt(api_client: APIClient, check_auth) -> Dict[str, Any]:
    """Create a test prompt for use in other tests."""
    if not GENERATE_DATA:
        pytest.skip("Data generation is disabled")

    prompt_data = DataGenerator.generate_prompt()
    response = api_client.post("/api/prompts/", json=prompt_data)
    return response


@pytest.fixture(scope="session")
def test_dataset(api_client: APIClient, check_auth) -> Dict[str, Any]:
    """Create a test dataset for use in other tests."""
    if not GENERATE_DATA:
        pytest.skip("Data generation is disabled")

    # Create CSV file content
    csv_content = DataGenerator.generate_csv_content(rows=5, dataset_type="question_answer")

    # Create temporary file
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp_file:
        temp_file.write(csv_content.encode('utf-8'))
        temp_path = temp_file.name

    try:
        # Create multipart form data
        files = {
            'file': ('test_data.csv', open(temp_path, 'rb'), 'text/csv')
        }
        data = {
            'name': f"Test Dataset {time.time()}",
            'description': "Dataset for automated tests",
            'type': "question_answer",
            'is_public': "true"
        }

        # Upload dataset
        response = api_client.post("/api/datasets/", data=data, files=files)
        return response
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.unlink(temp_path)


@pytest.fixture(scope="session")
def test_evaluation(api_client: APIClient, test_agent: Dict[str, Any],
                    test_dataset: Dict[str, Any], test_prompt: Dict[str, Any], check_auth) -> Dict[str, Any]:
    """Create a test evaluation for use in other tests."""
    if not GENERATE_DATA:
        pytest.skip("Data generation is disabled")

    eval_data = DataGenerator.generate_evaluation(
        agent_id=test_agent["id"],
        dataset_id=test_dataset["id"],
        prompt_id=test_prompt["id"]
    )

    response = api_client.post("/api/evaluations/", json=eval_data)
    return response


@pytest.fixture(scope="session")
def test_report(api_client: APIClient, test_evaluation: Dict[str, Any], check_auth) -> Dict[str, Any]:
    """Create a test report for use in other tests."""
    if not GENERATE_DATA:
        pytest.skip("Data generation is disabled")

    report_data = DataGenerator.generate_report(evaluation_id=test_evaluation["id"])

    response = api_client.post("/api/reports/", json=report_data)
    return response


# Configure test report output
@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    """Configure pytest with custom options."""
    # Register custom markers
    config.addinivalue_line("markers", "auth: tests for authentication endpoints")
    config.addinivalue_line("markers", "agents: tests for agent endpoints")
    config.addinivalue_line("markers", "datasets: tests for dataset endpoints")
    config.addinivalue_line("markers", "evaluations: tests for evaluation endpoints")
    config.addinivalue_line("markers", "prompts: tests for prompt endpoints")
    config.addinivalue_line("markers", "reports: tests for report endpoints")


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    """Generate a test report when the session finishes."""
    # Collect test statistics
    passed = session.testscollection.passed
    failed = session.testscollection.failed
    skipped = session.testscollection.skipped
    total = passed + failed + skipped

    # Group by module
    modules = {}
    for item in session.items:
        module_name = item.module.__name__.split(".")[-1]
        if module_name not in modules:
            modules[module_name] = {"total": 0, "passed": 0, "failed": 0, "skipped": 0}

        modules[module_name]["total"] += 1

        # Check outcome
        if hasattr(item, "_report_sections"):
            if any("failed" in section[2] for section in item._report_sections):
                modules[module_name]["failed"] += 1
            elif any("skipped" in section[2] for section in item._report_sections):
                modules[module_name]["skipped"] += 1
            else:
                modules[module_name]["passed"] += 1

    # Create report
    report = {
        "total": total,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "modules": modules,
        "duration": getattr(session, "duration", 0),
        "started_at": getattr(session, "started", ""),
        "failures": []
    }

    # Add failure details
    for item in session.items:
        if hasattr(item, "_report_sections") and any("failed" in section[2] for section in item._report_sections):
            failure = {
                "name": item.name,
                "module": item.module.__name__,
                "message": "",
                "traceback": ""
            }

            for section in item._report_sections:
                if section[0] == "call" and section[1] == "longrepr":
                    failure["traceback"] = section[2]
                    # Extract message from traceback
                    lines = section[2].split("\n")
                    if lines and "E " in section[2]:
                        for line in lines:
                            if line.startswith("E "):
                                failure["message"] = line[2:].strip()
                                break

            report["failures"].append(failure)

    # Create reports directory if it doesn't exist
    os.makedirs("reports", exist_ok=True)

    # Write report to file
    with open("reports/latest_results.json", "w") as f:
        json.dump(report, f, indent=2)