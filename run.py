#!/usr/bin/env python
"""The run script"""
import logging

from flywheel_gear_toolkit import GearToolkitContext


from fw_gear_file_validator.main import run
from fw_gear_file_validator.parser import parse_config
from fw_gear_file_validator.utils import (
    create_metadata,
    save_errors,
    make_fw_metadata_file,
    add_flywheel_location_to_errors,
)


log = logging.getLogger(__name__)


def main(context: GearToolkitContext) -> None:  # pragma: no cover
    """Parses gear config, runs main algorithm, and performs flywheel-specific actions."""

    # Call parse_config to extract the args, kwargs from the context
    # (e.g. config.json).
    (
        debug,
        tag,
        validation_level,
        schema_file_path,
        schema_file_type,
        input_file_object,
        input_file_path,
        input_file_type,
    ) = parse_config(context)

    # Generate a flywheel hierarchy json regardless of the level, it will be used
    # to populate flywheel hierarchy information later on of there are errors,
    # even if just the file is being validated.
    flywheel_hierarchy_path = make_fw_metadata_file(context, input_file_object)
    if validation_level == "flywheel":
        input_file_path = flywheel_hierarchy_path
        input_file_type = "json"

    valid, errors = run(
        schema_file_path,
        schema_file_type,
        input_file_path,
        input_file_type,
        context.output_dir,
    )

    # I'm sacrificing the simplicity of the run.py main function for the separation of generic validation vs
    # flywheel specific stuff.  In my mind, the run.py has always been the wrapper to what should be a flywheel-agnostic
    # algorithm, and flywheel specific things should go in here.
    errors = add_flywheel_location_to_errors(
        flywheel_hierarchy_path, validation_level, errors
    )
    save_errors(flywheel_hierarchy_path, errors, validation_level, context.output_dir)

    create_metadata(context, valid, input_file_object)
    context.metadata.add_file_tags(input_file_object, str(tag))


# Only execute if file is run as main, not when imported by another module
if __name__ == "__main__":  # pragma: no cover
    # Get access to gear config, inputs, and sdk client if enabled.
    with GearToolkitContext() as gear_context:
        # Initialize logging, set logging level based on `debug` configuration
        # key in gear config.
        gear_context.init_logging()

        # Pass the gear context into main function defined above.
        main(gear_context)
