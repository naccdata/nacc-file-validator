#!/usr/bin/env python
"""The run script"""
import logging

from flywheel_gear_toolkit import GearToolkitContext

from fw_gear_file_validator import validator
from fw_gear_file_validator.errors import add_flywheel_location_to_errors, save_errors
from fw_gear_file_validator.loader import Loader
from fw_gear_file_validator.parser import parse_config
from fw_gear_file_validator.utils import handle_metadata

log = logging.getLogger(__name__)


def main(context: GearToolkitContext) -> None:  # pragma: no cover
    """Parses gear config, runs main algorithm, and performs flywheel-specific actions."""

    (debug, tag, schema_file_path, fw_ref, loader_config) = parse_config(context)

    loader_type = fw_ref.file_type if fw_ref.validate_file_contents() else "flywheel"
    loader = Loader.factory(loader_type, config=loader_config)
    d = loader.load_object(fw_ref.loc())
    schema = loader.load_schema(schema_file_path)

    schema_validator = validator.JsonValidator(schema)
    valid, errors = schema_validator.validate(d)

    if fw_ref.is_file():
        error_filemame = f"{fw_ref.file_name}-validation-errors.json"
    else:
        error_filemame = "validation-errors.json"
    errors = add_flywheel_location_to_errors(fw_ref, errors)
    save_errors(errors, context.output_dir, error_filemame)
    handle_metadata(context, fw_ref, valid, tag)


if __name__ == "__main__":  # pragma: no cover
    with GearToolkitContext() as gear_context:
        gear_context.init_logging()
        main(gear_context)
