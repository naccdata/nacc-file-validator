import json
import typing as t
from pathlib import Path

import jsonschema
from jsonschema.exceptions import ValidationError


class JsonValidator:
    """Validator class."""

    def __init__(self, schema: t.Union[dict, Path, str]):
        if isinstance(schema, str):
            schema = Path(schema)
        if isinstance(schema, Path):
            with open(schema, "r", encoding="UTF-8") as schema_instance:
                schema = json.load(schema_instance)

        self.validator = jsonschema.Draft7Validator(schema)

    def validate(self, d: dict) -> t.Tuple[bool, t.List[t.Dict]]:
        valid, errors = self.process(d)
        return valid, errors

    def process(
        self, d: dict, reformat_error: bool = True
    ) -> t.Tuple[bool, t.List[t.Dict]]:
        """Validates a dict and returns a tuple of valid and formatted errors."""
        errors = list(self.validator.iter_errors(d))
        valid = False if errors else True
        if errors and reformat_error:
            errors = self.handle_errors(errors)
        return valid, errors

    @staticmethod
    def handle_errors(errors: list[ValidationError]) -> t.List[t.Dict]:
        """Processes errors into a standard output format.
        A jsonschema error in python has the following data structure:
        {
            'message': '[1, 2, 3, 4] is too long',
             'path': deque(['list']),
             'relative_path': deque(['list']),
             'schema_path': deque(['properties', 'list', 'maxItems']),
             'relative_schema_path': deque(['properties', 'list', 'maxItems']),
             'context': [],
             'cause': None,
             'validator': 'maxItems',
             'validator_value': 3,
             'instance': [1, 2, 3, 4],
             'schema': {'type': 'array', 'maxItems': 3},
             'parent': None,
             '_type_checker': <TypeChecker types={'array', 'boolean', 'integer', 'null', 'number', 'object', 'string'}>
         }

        This must be converted to the FW Error standard:
        type: str – “error” (always error)
        code: str – Type of the error (e.g. MaxLength)
        location: str – Location of the error
        flywheel_path: str – Flywheel path to the container/file
        container_id: str – ID of the source container/file
        value: str – current value
        expected: str – expected value
        message: str – error message description
        Additionally, the value for location will be formatted as such:
        For JSON input file: { “key_path”: string }, with string being the JSON key

        The flywheel relative items will be handled by a later function.
        They are omitted here to keep json validator flywheel client independent.
        These items are:
            - flywheel_path
            - container_id

        """

        errors = sorted(errors, key=lambda e: e.path)

        error_report = []
        for error in errors:
            error_report.append(
                {
                    "type": "error",  # For now, jsonValidaor can only produce errors.
                    "code": str(error.validator),
                    "location": {"key_path": ".".join(list(error.schema_path)[:-1])},
                    "value": str(error.instance),
                    "expected": str(error.schema),
                    "message": error.message,
                }
            )
        return error_report
