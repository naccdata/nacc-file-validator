import typing as t
from pathlib import Path
import json

import jsonschema


class JsonValidator:
    """Validator base class."""

    def __init__(self, schema: t.Union[dict, Path]):
        if isinstance(schema, Path):
            with open(schema, "r", encoding="UTF-8") as schema_instance:
                schema = json.load(schema_instance)

        self.validator = jsonschema.Draft7Validator(schema)

    def validate(self, json_object: dict) -> t.Tuple[bool, t.List[t.Dict]]:
        valid, errors = self.process(json_object)
        return valid, errors

    def process(self, json_object: dict) -> t.Tuple[bool, t.List[t.Dict]]:
        """validates a json dict object."""

        valid = self.validator.is_valid(json_object)
        if valid:
            return valid, [{}]
        errors = self.validator.iter_errors(json_object)
        packaged_errors = self.handle_errors(errors)
        return valid, packaged_errors

    @staticmethod
    def handle_errors(
        json_schema_errors: t.Generator[
            jsonschema.exceptions.ValidationError, None, None
        ]
    ) -> t.List[t.Dict]:
        """Processes errors into a standard output format."""

        errors = sorted(json_schema_errors, key=lambda e: e.path)
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
