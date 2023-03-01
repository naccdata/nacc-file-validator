#!/usr/bin/env python
"""The run script"""
import logging
import sys

from flywheel_gear_toolkit import GearToolkitContext

# This design with a separate main and parser module
# allows the gear to be publishable and the main interfaces
# to it can then be imported in another project which enables
# chaining multiple gears together.
from fw_gear_file_validator.main import run
from fw_gear_file_validator.parser import parse_config
from fw_gear_file_validator.utils import create_metadata

# The run.py should be as minimal as possible.
# The gear is split up into 2 main components. The run.py file which is executed
# when the container runs. The run.py file then imports the rest of the gear as a
# module.


log = logging.getLogger(__name__)


def main(context: GearToolkitContext) -> None:  # pragma: no cover
    """Parses gear config and run"""

    # Call parse_config to extract the args, kwargs from the context
    # (e.g. config.json).
    debug, tag, schema_file, schema_file_type, input_file_object, input_file_path = parse_config(
        context
    )

    valid = run(
        schema_file["location"]["path"],
        schema_file_type,
        input_file_path,
        context.output_dir,
    )

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
