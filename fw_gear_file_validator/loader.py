"""loader.py.

Functions relating to loading files.
"""

import csv
import json
import typing as t
from abc import ABC, abstractmethod
from pathlib import Path

from flywheel_gear_toolkit.utils.datatypes import Container

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
    def load_object(self, file: t.Union[Path, dict]) -> dict:
        """Returns the object to be validated as a dict."""
        pass


class JsonLoader(Loader):
    """Loads a JSON file."""

    name = "json"
    has_config = False

    def __init__(self):
        """Yet another extremely complicated function worthy of a docstring."""
        super().__init__()

    def load_object(self, file_path: Path) -> dict:
        """Returns the content of the JSON file as a dict."""
        try:
            # Check for empty file
            if file_path.stat().st_size == 0:
                return {}
            with open(file_path, "r", encoding="UTF-8") as fp:
                content = json.load(fp)
            return content
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise ValueError(f"Error loading JSON object: {e}")


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

    def load_object(self, fw_hierarchy: dict) -> dict:
        """Returns the content of the Flywheel reference as a dict."""
        if not self.add_parents:
            fw_hierarchy = {"file": fw_hierarchy["file"]}

        for k, container in fw_hierarchy.items():
            fw_hierarchy[k] = self._filter_container(container)
        return fw_hierarchy

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

    def load_object(self, file_path: Path) -> t.List[t.Dict]:
        """Returns the content of the csv file as a list of dicts."""
        try:
            self.validate_csv_headers(file_path)
            with open(file_path) as csv_file:
                csv_dict = [
                    {k: v for k, v in row.items() if v}
                    for row in csv.DictReader(csv_file)
                ]
                return list(csv_dict)
        except (FileNotFoundError, TypeError) as e:
            raise ValueError(f"Error loading CSV object: {e}")
        
    @staticmethod
    def validate_csv_headers(csv_path: Path) -> None:
        """Validates that the headers in the CSV file match the schema."""
        with open(csv_path) as csv_file:
            csv_headers = csv.DictReader(csv_file).fieldnames
            if not csv_headers:
                return
        if len(csv_headers) != len(set(csv_headers)):
            raise ValueError("CSV file contains duplicate headers")
