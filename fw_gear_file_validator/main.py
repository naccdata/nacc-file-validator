"""Main module."""

import logging
import typing as t
from pathlib import Path

from fw_gear_file_validator.validator_utils import validator, file_loaders
from fw_gear_file_validator.parser import identify_file_type
log = logging.getLogger(__name__)


def run(
    schema: t.Union[Path, t.Dict],
    input_object: t.Union[Path, t.Dict],
) -> t.Tuple[bool, t.List[t.Dict]]:
    """runs the validation and returns valid (T|F) and packaged errors

    Args:
        schema: the location of the schema file to use for validation
        schema_file_type: the type of schema file to be used to determine validation strategy
        input_object: the location of the file to validate

    Returns:
        valid: True if the file passed validation, False otherwise

    """
    if isinstance(input_object, Path):
        input_type = identify_file_type(input_object)
        loader = file_loaders.FileLoader.factory(input_type)
        input_object = loader.load(input_object)

    # Schema loading is handled in the validator if necessary, also accepts dict object
    schema_validator = validator.JsonValidator(schema)
    valid, errors = schema_validator.validate(input_object)

    return valid, errors
