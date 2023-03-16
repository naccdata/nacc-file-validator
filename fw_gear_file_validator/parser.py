"""Parser module to parse gear config.json."""

import os
import typing as t
from pathlib import Path

from flywheel_gear_toolkit import GearToolkitContext

from fw_gear_file_validator.env import (
    SUPPORTED_FILE_EXTENSIONS,
    SUPPORTED_FLYWHEEL_MIMETYPES,
)


level_dict = {"Validate File Contents": "file", "Validate Flywheel Objects": "flywheel"}


# This function mainly parses gear_context's config.json file and returns relevant
# inputs and options.
def parse_config(
    gear_context: GearToolkitContext,
) -> t.Tuple[bool, str, str, Path, str, dict, Path, str]:
    """parses necessary items out of the context object"""
    print(gear_context.config)
    debug = gear_context.config.get("debug")
    tag = gear_context.config.get("tag", "file-validator")
    validaton_level = gear_context.config.get("validation_level")
    validaton_level = level_dict[validaton_level]

    schema_file_object = gear_context.get_input("validation_schema")
    schema_file_type = identify_file_type(schema_file_object)
    schema_file_path = schema_file_object["location"]["path"]

    input_file_object = gear_context.get_input("input_file")
    if not input_file_object:
        # TODO: Do things here to validate the container that it's launched from
        pass
    else:
        input_file_path = input_file_object["location"]["path"]
        input_file_type = identify_file_type(input_file_object)

    return (
        debug,
        tag,
        validaton_level,
        schema_file_path,
        schema_file_type,
        input_file_object,
        input_file_path,
        input_file_type,
    )


def identify_file_type(input_file: dict) -> str:
    """Given a flywheel config input file object, identify the file type."""
    # First try to just check the file type from the file extension:
    file_name = input_file["location"]["name"]
    base, ext = os.path.splitext(file_name)
    if ext:
        input_file_type = SUPPORTED_FILE_EXTENSIONS.get(ext)
        if input_file_type is None:
            raise TypeError(f"file type {ext} is not supported")
        return input_file_type

    mime = input_file["object"]["mimetype"]
    input_file_type = SUPPORTED_FLYWHEEL_MIMETYPES.get(mime)
    if input_file_type is None:
        raise TypeError(f"file type {mime} is not supported")
    return input_file_type
