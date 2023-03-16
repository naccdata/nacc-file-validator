import typing as t
from pathlib import Path

import jsonschema

from .loaders import Loader


class JsonValidator:
    """Validator base class."""

    def __init__(self, schema_file_path: t.Union[str, Path], loader: Loader):
        self.schema_file_path = schema_file_path
        self.schema_loader = loader

    def validate(self, file_object: t.Any) -> t.Tuple[bool, t.List[t.Dict]]:
        valid, errors = self.process(file_object)
        return valid, errors

    def process(self, file_object: t.Dict) -> t.Tuple[bool, t.List[t.Dict]]:
        """validates a json dict object."""

        schema = self.schema_loader(self.schema_file_path).load()
        validator = jsonschema.Draft7Validator(schema)
        valid = validator.is_valid(file_object)
        if valid:
            return valid, {}
        errors = validator.iter_errors(file_object)
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

