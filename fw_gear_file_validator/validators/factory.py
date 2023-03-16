import typing as t
from pathlib import Path

from .loaders import JsonLoader, Loader
from .validator import JsonValidator, Validator

VALIDATOR_FACTORY_MAP = {"json": JsonValidator}
LOADER_FACTORY_MAP = {"json": JsonLoader}


def loader_factory(input_type: str) -> Loader:
    """Factory function to return the correct file loader, based on file type."""
    loader_class = LOADER_FACTORY_MAP.get(input_type)
    if not loader_class:
        raise NotImplementedError(f"File type {input_type} not supported for loader")
    return loader_class


def validator_factory(
    schema_file_path: t.Union[str, Path], schema_type: str
) -> Validator:
    """Factory function to return the correct validator object, based on schema type."""
    validator_class = VALIDATOR_FACTORY_MAP.get(schema_type)
    loader_class = loader_factory(schema_type)

    if not validator_class:
        raise NotImplementedError(
            f"File type {schema_type} not supported for validator"
        )

    return validator_class(schema_file_path, loader_class)
