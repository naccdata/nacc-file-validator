import json
from abc import ABC, abstractmethod
from pathlib import Path

# TODO: Loader will have file path and optional file typu input.  If type not given, figure it out


class FileLoader(ABC):
    name = None

    @classmethod
    def factory(cls, name):
        for subclass in cls.__subclasses__():
            if subclass.name == name:
                loader = subclass()
                return loader

        raise ValueError(f"Type {name} not supported")

    @staticmethod
    @abstractmethod
    def load(file_path: Path):
        pass


class JsonLoader(FileLoader):
    name = "json"

    @staticmethod
    def load(file_path: Path):
        with open(file_path, "r", encoding="UTF-8") as file_instance:
            file_object = json.load(file_instance)
        return file_object
