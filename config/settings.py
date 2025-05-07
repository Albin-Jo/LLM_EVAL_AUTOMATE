import os
import json
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
REPORT_DIR = BASE_DIR / "reports"
REPORT_DIR.mkdir(exist_ok=True)

# API configuration
API_BASE_URL = os.environ.get("LLM_API_BASE_URL", "http://localhost:8000")
API_TOKEN = os.environ.get("LLM_API_TOKEN", "")
API_TIMEOUT = int(os.environ.get("LLM_API_TIMEOUT", "30"))

# Test configuration
GENERATE_DATA = os.environ.get("LLM_GENERATE_DATA", "True").lower() != "false"
PARALLEL_EXECUTION = os.environ.get("LLM_PARALLEL_EXECUTION", "False").lower() == "true"
LOG_LEVEL = os.environ.get("LLM_LOG_LEVEL", "INFO")

# Schema configuration
SCHEMA_PATH = os.environ.get("LLM_SCHEMA_PATH", str(BASE_DIR / "openapi.json"))

# Reporting configuration
REPORT_FORMAT = os.environ.get("LLM_REPORT_FORMAT", "html")
REPORT_TITLE = os.environ.get("LLM_REPORT_TITLE", "LLM API Test Report")


class Config:
    """Configuration container with methods for loading and validating config."""

    @staticmethod
    def load_schema() -> Optional[Dict[str, Any]]:
        """Load the OpenAPI schema if available."""
        schema_path = SCHEMA_PATH
        if os.path.exists(schema_path):
            try:
                with open(schema_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading schema from {schema_path}: {e}")
        return None

    @staticmethod
    def get_api_url(endpoint: str) -> str:
        """Build a full API URL for the given endpoint."""
        base = API_BASE_URL.rstrip("/")
        endpoint = endpoint.lstrip("/")
        return f"{base}/{endpoint}" if endpoint else base

    @staticmethod
    def get_auth_headers() -> Dict[str, str]:
        """Get authentication headers for API requests."""
        headers = {}
        if API_TOKEN:
            headers["Authorization"] = f"Bearer {API_TOKEN}"
        return headers

    @staticmethod
    def get_report_path(report_name: str, extension: Optional[str] = None) -> str:
        """Get the full path for a report file."""
        ext = extension or REPORT_FORMAT
        if not ext.startswith("."):
            ext = f".{ext}"
        return str(REPORT_DIR / f"{report_name}{ext}")