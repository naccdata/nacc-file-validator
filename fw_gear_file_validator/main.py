"""Main module."""

import logging
from pathlib import Path
import typing as t
from fw_gear_file_validator.validators import factory
from fw_gear_file_validator.utils import save_errors

log = logging.getLogger(__name__)


def run(schema_file_path: t.Union[str, Path], schema_file_type: str, input_file_path: t.Union[str, Path], output_dir: t.Union[str, Path]) -> bool:
    """

    Args:
        schema_file_path: the location of the schema file to use for validation
        schema_file_type: the type of schema file to be used to determine validation strategy
        input_file_path: the location of the file to validate
        output_dir: the direcory to save outputs in (error csv file)

    Returns:
        valid: True if the file passed validation, False otherwise

    """
    log.info("This is the beginning of the run file")

    validator_factory = factory.ValidatorFactory(schema_file_path, schema_file_type)
    validator = validator_factory.get_type_validator()
    valid, errors = validator.validate(Path(input_file_path))
    save_errors(errors, output_dir)

    return valid
