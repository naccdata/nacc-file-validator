#!/usr/bin/env python
"""The run script"""
import logging

from flywheel_gear_toolkit import GearToolkitContext

from fw_gear_file_validator.main import run
from fw_gear_file_validator.parser import parse_config
from fw_gear_file_validator.utils import (
    add_flywheel_location_to_errors,
    handle_metadata,
    save_errors,
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
        schema,
        input_json,
        flywheel_hierarchy,
        strategy,
    ) = parse_config(context)

    # Generate a flywheel hierarchy json regardless of the level, it will be used
    # to populate flywheel hierarchy information later on of there are errors,
    # even if just the file is being validated.

    valid, errors = run(schema, input_json)

    errors = add_flywheel_location_to_errors(
        flywheel_hierarchy, validation_level, errors
    )
    save_errors(errors, context.output_dir)

    handle_metadata(context, strategy, valid, tag)


# Only execute if file is run as main, not when imported by another module
if __name__ == "__main__":  # pragma: no cover
    # Get access to gear config, inputs, and sdk client if enabled.
    with GearToolkitContext() as gear_context:
        # Initialize logging, set logging level based on `debug` configuration
        # key in gear config.
        gear_context.init_logging()

        # Pass the gear context into main function defined above.
        main(gear_context)
