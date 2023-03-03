import typing as t
from abc import ABC, abstractmethod
from pathlib import Path

import fw_file

from .loaders import Loader


class Validator(ABC):
    def __init__(self, schema_file_path: t.Union[str, Path], loader: Loader):
        self.schema_file_path = schema_file_path
        self.schema_loader = loader

    @abstractmethod
    def process(self, file_object: t.Any) -> (bool, dict):
        pass

    def validate(self, file_object: t.Any) -> t.Tuple[bool, t.List[t.Dict]]:
        valid, errors = self.process(file_object)
        return valid, errors


class JsonValidator(Validator):
    import jsonschema

    def process(self, file_object: t.Dict) -> t.Tuple[bool, t.List[t.Dict]]:
        import jsonschema

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
