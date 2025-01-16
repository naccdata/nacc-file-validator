"""loader.py.

Functions relating to loading files.
"""

import csv
import io
import json
import typing as t
from abc import ABC, abstractmethod
from pathlib import Path

from flywheel_gear_toolkit.utils.datatypes import Container

import fw_gear_file_validator.errors as err

PARENT_INCLUDE = [
    # General values
    "label",
    "info",
    "uid",
    # Session values
    "age",
    "weight",
    # Subject values
    "sex",
    "cohort",
    "mlset",
    "ethnicity",
    "species",
    "strain",
    "code",
    "firstname",
    "lastname",
]


class Loader(ABC):
    """Abstract base class for loaders.

    This is used to load the schema and the object to be validated.
    """

    name = None
    has_config = False

    @classmethod
    def factory(cls, name: str, config: t.Dict[str, t.Any] = None) -> "Loader":
        """Returns a configured loader based on the name and config provided."""
        loader = None
        for subclass in cls.__subclasses__():
            if subclass.name == name:
                if subclass.has_config:
                    loader = subclass(config)
                else:
                    loader = subclass()
                break

        if not loader:
            raise ValueError(f"Loader {name} not found")

        return loader

    @staticmethod
    def load_schema(file_path: Path) -> dict:
        """Method for loading a json schema to use for validation.

        Args:
            file_path: The path of the json schema.

        Returns:
            dict: the schema in dict format.

        """
        return JsonLoader().load_object(file_path)

    @abstractmethod
    def load_object(self, file: t.Union[Path, dict]) -> t.Tuple[dict, t.List[t.Dict]]:
        """Returns the object to be validated as a dict. Performs file structure validation."""
        pass

    @staticmethod
    def handle_errors(file_errors: list[err.ValidationError]) -> t.List[t.Dict]:
        error_report = []
        for error in file_errors:
            error_report.append(err.validator_error_to_standard(error))
        return error_report


class JsonLoader(Loader):
    """Loads a JSON file."""

    name = "json"
    has_config = False

    def __init__(self):
        """Yet another extremely complicated function worthy of a docstring."""
        super().__init__()

    def load_object(self, file_path: Path) -> t.Tuple[dict, t.List[t.Dict]]:
        """Returns the content of the JSON file as a dict."""
        try:
            # Check for empty file
            format_errors = self.validate_file_format(file_path)
            if format_errors:
                return None, format_errors
            with open(file_path, "r", encoding="UTF-8") as fp:
                content = json.load(fp)
            return content, None
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise ValueError(f"Error loading JSON object: {e}")

    def validate_file_format(
        self, file_path: Path
    ) -> t.Union[err.ValidationError, None]:
        """Validates some basic file format items."""
        errors = []

        if file_path.stat().st_size == 0:
            errors.append(err.make_empty_file_error())

        if errors:
            return self.handle_errors(errors)

        return None


class FwLoader(Loader):
    """Loads a Flywheel object."""

    name = "flywheel"
    has_config = True

    def __init__(self, config: t.Dict[str, t.Any]):
        """Initializes a FwLoader object.

        I realize this is an extremely difficult function to read, so here,
        the docstring will help you decipher this cryptic code:
        this initializes an object for loading a flywheel object,
        with or without its parents.

        Args:
            config: the loader config
        """
        self.add_parents = config.get("add_parents")

    def load_object(self, fw_hierarchy: dict) -> t.Tuple[dict, t.List[t.Dict]]:
        """Returns the content of the Flywheel reference as a dict."""
        # currently no validation here
        if not self.add_parents:
            fw_hierarchy = {"file": fw_hierarchy["file"]}

        for k, container in fw_hierarchy.items():
            fw_hierarchy[k] = self._filter_container(container)
        return fw_hierarchy, None

    @staticmethod
    def _filter_container(container: Container):
        """Filters the container to remove unwanted fields."""
        cont_f = {k: v for k, v in container.to_dict().items() if k in PARENT_INCLUDE}
        return cont_f


class CsvLoader(Loader):
    """Loads a csv object."""

    name = "csv"
    has_config = False

    def __init__(self):
        """Surprisingly this does not initialize this class.  NO, OF COURSE IT DOES, WHY DO I NEED A DOCSTRING?"""
        super().__init__()

    def load_object(self, file_path: Path) -> t.Tuple[t.List[t.Dict], t.List[t.Dict]]:
        """Returns the content of the csv file as a list of dicts."""
        try:
            format_errors = self.validate_file_format(file_path)
            if format_errors:
                return None, format_errors
            with open(file_path) as csv_file:
                csv_dict = [
                    {k: v for k, v in row.items() if v}
                    for row in csv.DictReader(csv_file)
                ]
                return list(csv_dict), None
        except (FileNotFoundError, TypeError) as e:
            raise ValueError(f"Error loading CSV object: {e}")

    def validate_file_format(
        self, csv_path: Path
    ) -> t.Union[err.ValidationError, None]:
        """Validates some basic file format items."""
        errors = []
        try:
            with open(csv_path) as csv_file:
                # First check to see if we have the correct number of commas in each row
                syntax_errors = self.validate_num_commas(csv_file)
                if syntax_errors:
                    errors.append(syntax_errors)
                # Then check to see if any headers are duplicated
                csv_file.seek(0)
                header_errors = self.validate_file_header(csv_file)
                if header_errors:
                    errors.append(header_errors)
        # If we had an error here loading the file or otherwise, captuer that.
        except Exception as e:
            unknown_error = err.make_malformed_file_error()
            unknown_error.message = str(e)
            errors.append(unknown_error)

        if errors:
            return self.handle_errors(errors)
        return None

    @staticmethod
    def validate_num_commas(
        csv_file: io.TextIOWrapper,
    ) -> t.Union[err.ValidationError, None]:
        """Validates that the number of commas in each row is consistent."""
        first_line = csv_file.readline().strip()
        commas_in_header = first_line.count(",")
        line_num = 1
        for line in csv_file:
            if line.count(",") != commas_in_header:
                error = err.make_malformed_file_error()
                error.message = (
                    "The number of commas in row %s do not match the number of headers."
                    % line_num
                )
                return error
            line_num += 1
        return None

    @staticmethod
    def validate_file_header(
        csv_file: io.TextIOWrapper,
    ) -> t.Union[err.ValidationError, None]:
        first_line = csv_file.readline().strip()
        if not first_line:
            return err.make_empty_file_error()
        csv_headers = first_line.split(",")
        if len(csv_headers) != len(set(csv_headers)):
            return err.make_duplicate_header_error()
        return None
