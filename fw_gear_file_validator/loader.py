import json
import typing as t
from abc import ABC, abstractmethod
from pathlib import Path
import pandas as pd

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
    This is used to load the schema and the object to be validated."""

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
        super().__init__()

    def load_object(self, file_path: Path) -> dict:
        """Returns the content of the JSON file as a dict."""
        try:
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

    def __init__(self, config: t.Dict[str, t.Any]):
        super().__init__()

    def load_object(self, file_path: Path) -> dict:
        """Returns the content of the Flywheel reference as a dict."""
        try:
            dataframe = pd.read_csv(file_path)
            return dataframe
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise ValueError(f"Error loading JSON object: {e}")



def test_new_loader(file_path: Path, delimiter=","):
    import csv

    with open(file_path) as file:
        lines = [line.rstrip() for line in file]

    headers = lines.pop(0).split(delimiter)
    new_lines = []
    for line in lines:
        new_line = line.split(delimiter)
        new_line = ['"' + h + '"' + ": " + v for h, v in zip(headers, new_line)]
        new_line = "{" + delimiter.join(new_line) + "},"
        new_lines.append(new_line)

    new_file_path = file_path + ".json"
    with open(new_file_path, 'w') as new_file:
        new_file.write("[")
        new_file.writelines(new_lines)
        new_file.write("]")



    with open(file_path) as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',')
        header = csv_reader.__next__()
        json_csv = []
        for row in csv_reader:
            json_csv.append({k : v for k, v in zip(header, row)})

