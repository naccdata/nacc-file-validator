import typing as t
from abc import ABC, abstractmethod
from pathlib import Path


# TODO: Make use of fw_file for loading when json module is merged
class Loader(ABC):
    def __init__(self, path_to_file: Path) -> None:
        self.path = path_to_file

    @abstractmethod
    def load(self) -> t.Any:
        pass


class JsonLoader(Loader):
    def __init__(self, path):
        super().__init__(path)

    def load(self):
        import json

        with open(self.path, "r", encoding="UTF-8") as file_instance:
            file_object = json.load(file_instance)
        return file_object
