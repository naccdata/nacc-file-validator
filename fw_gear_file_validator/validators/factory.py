from abc import ABC, abstractmethod
from pathlib import Path
import typing as t


class Validator(ABC):
    def __init__(self, schema_file_path: t.Union[str, Path]):
        self.schema_file_path = schema_file_path
        self.schema = self.load_schema(schema_file_path)

    @abstractmethod
    def load_schema(self, path: t.Union[str, Path]):
        pass

    @abstractmethod
    def process(self, file_object: t.Any) -> (bool, dict):
        pass

    @abstractmethod
    def load_file(self, file: t.Union[str, Path]) -> t.Any:
        pass

    def validate(self, file: Path) -> t.Tuple[bool, t.List[t.Dict]]:
        file_object = self.load_file(file)
        valid, errors = self.process(file_object)
        return valid, errors


class JsonValidator(Validator):
    import jsonschema

    def load_file(self, file: Path) -> t.Dict:
        return self.load_schema(file)

    def load_schema(self, path: t.Union[str, Path]) -> t.Dict:
        import json

        with open(path, "r") as file_instance:
            file_object = json.load(file_instance)
        return file_object

    def process(self, file_object: t.Dict) -> t.Tuple[bool, t.List[t.Dict]]:
        import jsonschema
        validator = jsonschema.Draft7Validator(self.schema)
        valid = validator.is_valid(file_object)
        if valid:
            return valid, {}
        errors = validator.iter_errors(file_object)
        packaged_errors = self.handle_errors(errors)
        return valid, packaged_errors

    @staticmethod
    def handle_errors(json_schema_errors: t.Generator[jsonschema.exceptions.ValidationError, None, None]) -> t.List[
        t.Dict]:
        errors = sorted(json_schema_errors, key=lambda e: e.path)
        error_report = []
        for error in errors:
            error_report.append(
                {
                    "item": ": ".join(error.absolute_schema_path),
                    "value": str(error.instance),
                    "allowed": str(error.schema),
                    "message": error.message,
                }
            )
        return error_report


class ValidatorFactory:
    def __init__(self, schema_file_path: t.Union[str, Path], schema_type: str) -> None:
        self.schema = schema_file_path
        self.factory_map = {"json": JsonValidator}
        self.schema_type = schema_type

    def get_type_validator(self) -> Validator:
        validator_class = self.factory_map[self.schema_type]
        return validator_class(self.schema)
