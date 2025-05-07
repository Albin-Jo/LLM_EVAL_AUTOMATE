import requests
import logging
from typing import Dict, Any, Optional, Union
from config.settings import API_BASE_URL

logger = logging.getLogger(__name__)


class APIClient:
    """Client for interacting with the LLM Evaluation Framework API."""

    def __init__(self, base_url: str = API_BASE_URL, token: Optional[str] = None):
        self.base_url = base_url
        self.token = token
        self.session = requests.Session()
        if token:
            self.session.headers.update({"Authorization": f"Bearer {token}"})

    def set_token(self, token: str) -> None:
        """Set the authentication token for future requests."""
        self.token = token
        self.session.headers.update({"Authorization": f"Bearer {token}"})

    def _build_url(self, endpoint: str) -> str:
        """Build the full URL for the given endpoint."""
        return f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle the response from the API."""
        try:
            response.raise_for_status()
            if response.content:
                return response.json()
            return {}
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP Error: {e}")
            logger.error(f"Response: {response.text}")
            raise
        except ValueError as e:
            logger.error(f"Error parsing response: {e}")
            logger.error(f"Response: {response.text}")
            raise

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send a GET request to the API."""
        url = self._build_url(endpoint)
        logger.info(f"GET {url}")
        response = self.session.get(url, params=params)
        return self._handle_response(response)

    def post(self, endpoint: str, json: Optional[Dict[str, Any]] = None, data: Optional[Dict[str, Any]] = None,
             files: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send a POST request to the API."""
        url = self._build_url(endpoint)
        logger.info(f"POST {url}")
        response = self.session.post(url, json=json, data=data, files=files)
        return self._handle_response(response)

    def put(self, endpoint: str, json: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send a PUT request to the API."""
        url = self._build_url(endpoint)
        logger.info(f"PUT {url}")
        response = self.session.put(url, json=json)
        return self._handle_response(response)

    def delete(self, endpoint: str) -> Dict[str, Any]:
        """Send a DELETE request to the API."""
        url = self._build_url(endpoint)
        logger.info(f"DELETE {url}")
        response = self.session.delete(url)
        return self._handle_response(response)