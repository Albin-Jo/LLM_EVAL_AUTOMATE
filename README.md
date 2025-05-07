# LLM API Test Automation Framework

A comprehensive framework for testing LLM Evaluation Framework APIs.

## Overview

This framework provides automated testing for the complete API surface of the LLM Evaluation Framework. It includes test coverage for all endpoints, data generation utilities, detailed reporting, and an optional UI for test management.

## Features

- **Comprehensive API Coverage**: Tests for all endpoints in the OpenAPI specification
- **Automated Test Data Generation**: Creates realistic test data for all resources
- **Dependency Management**: Handles dependencies between API resources
- **Detailed Reporting**: Generates comprehensive HTML and JSON reports with visualizations
- **User-Friendly UI**: Optional Streamlit interface for running tests and viewing results
- **Authentication Support**: Properly handles JWT authentication for protected endpoints
- **Validation**: Validates API responses against the OpenAPI schema
- **Flexible Configuration**: Supports different test configurations via environment variables

## Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`

## Installation

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd llm-api-test-framework
   

Usage
Run all tests:
python main.py test

Run specific test modules:
python main.py test --modules auth agents datasets

Run with authentication token:
python main.py test --token YOUR_JWT_TOKEN

Additional options:
python main.py test --help

Launch the UI:
python main.py ui


Key configuration options:

LLM_API_BASE_URL: Base URL for the API (default: http://localhost:8000)
LLM_API_TOKEN: JWT token for authentication
LLM_GENERATE_DATA: Enable/disable test data generation (default: True)
LLM_PARALLEL_EXECUTION: Enable/disable parallel test execution (default: False)
LLM_REPORT_FORMAT: Report format (html or json, default: html)
LLM_SCHEMA_PATH: Path to OpenAPI schema file