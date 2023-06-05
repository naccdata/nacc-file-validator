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
        """Processes errors into a standard output format."""

        errors = sorted(errors, key=lambda e: e.path)

        error_report = []
        for error in errors:
            error_report.append(
                {
                    "Error_Type": str(error.validator),
                    "Error_Location": str(".".join(error.path)),
                    "Value": str(error.instance),
                    "Expected": str(error.schema),
                    "Message": error.message,
                }
            )
        return error_report
