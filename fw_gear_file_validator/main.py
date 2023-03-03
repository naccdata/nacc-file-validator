"""Main module."""

import logging
import typing as t
from pathlib import Path

from fw_gear_file_validator.validators import factory
from fw_gear_file_validator.validators.loaders import Loader

log = logging.getLogger(__name__)


def run(
    schema_file_path: t.Union[str, Path],
    schema_file_type: str,
    input_file_path: t.Union[str, Path],
    input_file_type: str,
) -> t.Tuple[bool, t.List[t.Dict]]:
    """runs the validation and returns valid (T|F) and packaged errors

    Args:
        schema_file_path: the location of the schema file to use for validation
        schema_file_type: the type of schema file to be used to determine validation strategy
        input_file_path: the location of the file to validate
        output_dir: the direcory to save outputs in (error csv file)

    Returns:
        valid: True if the file passed validation, False otherwise

    """

    schema_validator = factory.validator_factory(schema_file_path, schema_file_type)
    file_loader = factory.loader_factory(input_file_type)

    file_object = file_loader(input_file_path).load()

    valid, errors = schema_validator.validate(file_object)

    return valid, errors
