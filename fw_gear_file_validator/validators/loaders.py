import typing as t
from abc import ABC, abstractmethod
from pathlib import Path


class Loader(ABC):
    """Base class for file loading object."""

    def __init__(self, path_to_file: Path) -> None:
        self.path = path_to_file

    @abstractmethod
    def load(self) -> t.Any:
        """Loads the file and returns it however it's best represented in python."""
        pass


class JsonLoader(Loader):
    """Json File loader object"""

    def __init__(self, path):
        super().__init__(path)

    def load(self) -> t.Dict:
        """Loads the file and returns it as a dict."""
        import json

        with open(self.path, "r", encoding="UTF-8") as file_instance:
            file_object = json.load(file_instance)
        return file_object
