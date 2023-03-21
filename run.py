#!/usr/bin/env python
"""The run script"""
import logging
from pathlib import Path

from flywheel_gear_toolkit import GearToolkitContext

from fw_gear_file_validator.main import run
from fw_gear_file_validator.parser import parse_config
from fw_gear_file_validator.flywheel_utils.flywheel_env import FwReference, FwLoaderConfig
from fw_gear_file_validator.flywheel_utils.metadata_utils import handle_metadata
from fw_gear_file_validator.flywheel_utils.error_parsing import add_flywheel_location_to_errors, save_errors
from fw_gear_file_validator.flywheel_utils.flywheel_loaders import FwLoader

log = logging.getLogger(__name__)


def prepare_fw_gear_json(context, config: FwLoaderConfig, fw_reference: FwReference):

    fw_loader = FwLoader(context, config)
    full_fw_meta, validation_dict = fw_loader.load(fw_reference)

    return full_fw_meta, validation_dict


def main(context: GearToolkitContext) -> None:  # pragma: no cover
    """Parses gear config, runs main algorithm, and performs flywheel-specific actions."""

    # Call parse_config to extract the args, kwargs from the context
    # (e.g. config.json).
    (
        debug,
        tag,
        validation_level,
        add_parents,
        schema_file_path,
        fw_reference,
    ) = parse_config(context)

    # Generate a flywheel hierarchy json regardless of the level, it will be used
    # to populate flywheel hierarchy information later on of there are errors,
    # even if just the file is being validated.
    config = FwLoaderConfig(add_parents, validation_level)
    fw_meta, input_json = prepare_fw_gear_json(context, config, fw_reference)
    valid, errors = run(schema_file_path, input_json)

    errors = add_flywheel_location_to_errors(
        fw_meta, validation_level, errors
    )

    save_errors(errors, context.output_dir)
    handle_metadata(errors, config, context, valid, tag)


# Only execute if file is run as main, not when imported by another module
if __name__ == "__main__":  # pragma: no cover
    # Get access to gear config, inputs, and sdk client if enabled.
    with GearToolkitContext() as gear_context:
        # Initialize logging, set logging level based on `debug` configuration
        # key in gear config.
        gear_context.init_logging()

        # Pass the gear context into main function defined above.
        main(gear_context)
