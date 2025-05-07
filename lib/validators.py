import json
import re
from typing import Dict, Any, List, Optional, Union, Set


class ResponseValidator:
    """Validate API responses against expected schemas."""

    def __init__(self, schema_path: Optional[str] = None):
        """Initialize with optional OpenAPI schema."""
        self.schema = None
        if schema_path:
            with open(schema_path, 'r') as f:
                self.schema = json.load(f)

    def get_schema_for_endpoint(self, method: str, path: str) -> Optional[Dict[str, Any]]:
        """Get the response schema for a specific endpoint and method."""
        if not self.schema:
            return None

        # Normalize path
        path = path.rstrip('/')
        if not path.startswith('/'):
            path = f"/{path}"

        # Check for exact path match
        if path in self.schema.get('paths', {}):
            endpoint_spec = self.schema['paths'][path]
            if method.lower() in endpoint_spec:
                return self._extract_response_schema(endpoint_spec[method.lower()])

        # Check for path parameter matches
        for schema_path, path_spec in self.schema.get('paths', {}).items():
            if self._match_path_pattern(path, schema_path):
                if method.lower() in path_spec:
                    return self._extract_response_schema(path_spec[method.lower()])

        return None

    def _match_path_pattern(self, actual_path: str, schema_path: str) -> bool:
        """Check if actual path matches a schema path pattern with parameters."""
        # Replace path parameters like {id} with regex patterns
        pattern = re.sub(r'\{([^}]+)\}', r'([^/]+)', schema_path)
        pattern = f"^{pattern}$"
        return bool(re.match(pattern, actual_path))

    def _extract_response_schema(self, method_spec: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract response schema from method specification."""
        responses = method_spec.get('responses', {})

        # Check for 200 or 201 response
        for status_code in ['200', '201']:
            if status_code in responses:
                response_spec = responses[status_code]
                if 'content' in response_spec:
                    content = response_spec['content']
                    if 'application/json' in content:
                        return content['application/json'].get('schema')

        return None

    def validate_response(self, response: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
        """Validate a response against a schema."""
        errors = []

        # Check for required properties
        required = schema.get('required', [])
        for prop in required:
            if prop not in response:
                errors.append(f"Missing required property: {prop}")

        # Check property types
        properties = schema.get('properties', {})
        for prop_name, prop_spec in properties.items():
            if prop_name in response:
                prop_errors = self._validate_property(prop_name, response[prop_name], prop_spec)
                errors.extend(prop_errors)

        return errors

    def _validate_property(self, name: str, value: Any, schema: Dict[str, Any]) -> List[str]:
        """Validate a single property against its schema."""
        errors = []

        # Handle nullable properties
        if value is None:
            if 'nullable' in schema and schema['nullable']:
                return []
            else:
                return [f"Property {name} cannot be null"]

        # Check type
        schema_type = schema.get('type')
        if schema_type:
            if schema_type == 'string':
                if not isinstance(value, str):
                    errors.append(f"Property {name} should be a string")
                else:
                    # Check string format if specified
                    if 'format' in schema:
                        format_errors = self._validate_string_format(name, value, schema['format'])
                        errors.extend(format_errors)

                    # Check string length constraints
                    if 'minLength' in schema and len(value) < schema['minLength']:
                        errors.append(f"Property {name} is too short (min: {schema['minLength']})")
                    if 'maxLength' in schema and len(value) > schema['maxLength']:
                        errors.append(f"Property {name} is too long (max: {schema['maxLength']})")

            elif schema_type == 'number' or schema_type == 'integer':
                if not isinstance(value, (int, float)):
                    errors.append(f"Property {name} should be a number")
                else:
                    # Check number constraints
                    if schema_type == 'integer' and not isinstance(value, int):
                        errors.append(f"Property {name} should be an integer")
                    if 'minimum' in schema and value < schema['minimum']:
                        errors.append(f"Property {name} is too small (min: {schema['minimum']})")
                    if 'maximum' in schema and value > schema['maximum']:
                        errors.append(f"Property {name} is too large (max: {schema['maximum']})")

            elif schema_type == 'boolean':
                if not isinstance(value, bool):
                    errors.append(f"Property {name} should be a boolean")

            elif schema_type == 'array':
                if not isinstance(value, list):
                    errors.append(f"Property {name} should be an array")
                else:
                    # Check array item types
                    if 'items' in schema:
                        for i, item in enumerate(value):
                            item_errors = self._validate_property(f"{name}[{i}]", item, schema['items'])
                            errors.extend(item_errors)

                    # Check array length constraints
                    if 'minItems' in schema and len(value) < schema['minItems']:
                        errors.append(f"Property {name} has too few items (min: {schema['minItems']})")
                    if 'maxItems' in schema and len(value) > schema['maxItems']:
                        errors.append(f"Property {name} has too many items (max: {schema['maxItems']})")

            elif schema_type == 'object':
                if not isinstance(value, dict):
                    errors.append(f"Property {name} should be an object")
                else:
                    # Check nested properties
                    if 'properties' in schema:
                        for prop_name, prop_spec in schema['properties'].items():
                            if prop_name in value:
                                prop_errors = self._validate_property(f"{name}.{prop_name}",
                                                                      value[prop_name], prop_spec)
                                errors.extend(prop_errors)

                    # Check required properties
                    if 'required' in schema:
                        for required_prop in schema['required']:
                            if required_prop not in value:
                                errors.append(f"Missing required property {name}.{required_prop}")

        # Handle anyOf, oneOf, allOf
        if 'anyOf' in schema:
            any_valid = False
            any_errors = []
            for sub_schema in schema['anyOf']:
                sub_errors = self._validate_property(name, value, sub_schema)
                if not sub_errors:
                    any_valid = True
                    break
                any_errors.extend(sub_errors)

            if not any_valid:
                errors.append(f"Property {name} does not match any allowed schemas")
                errors.extend([f"  - {err}" for err in any_errors])

        return errors

    def _validate_string_format(self, name: str, value: str, format_type: str) -> List[str]:
        """Validate a string against a specific format."""
        errors = []

        if format_type == 'date-time':
            # Simple ISO date-time format check
            if not re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', value):
                errors.append(f"Property {name} should be in ISO date-time format")

        elif format_type == 'email':
            # Simple email format check
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
                errors.append(f"Property {name} should be a valid email address")

        elif format_type == 'uuid':
            # UUID format check
            if not re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', value, re.I):
                errors.append(f"Property {name} should be a valid UUID")

        elif format_type == 'uri' or format_type == 'url':
            # Simple URL format check
            if not re.match(r'^https?://[^\s/$.?#].[^\s]*$', value):
                errors.append(f"Property {name} should be a valid URL")

        return errors