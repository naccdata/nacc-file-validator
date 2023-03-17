"""Parser module to parse gear config.json."""

import os
import typing as t
from pathlib import Path
import json

from flywheel_gear_toolkit import GearToolkitContext

from fw_gear_file_validator.env import (
    SUPPORTED_FILE_EXTENSIONS,
    SUPPORTED_FLYWHEEL_MIMETYPES,
)
from fw_gear_file_validator.validators import loaders

level_dict = {"Validate File Contents": "file", "Validate Flywheel Objects": "flywheel"}


# This function mainly parses gear_context's config.json file and returns relevant
# inputs and options.
def parse_config(
    gear_context: GearToolkitContext,
) -> t.Tuple[bool, str, str, dict, dict, dict, str]:
    """parses necessary items out of the context object"""
    debug = gear_context.config.get("debug")
    tag = gear_context.config.get("tag", "file-validator")
    add_parents = gear_context.config.get("add_parents")
    validation_level = gear_context.config.get("validation_level")
    validation_level = level_dict[validation_level]

    schema_file_object = gear_context.get_input("validation_schema")
    schema_file_path = schema_file_object["location"]["path"]
    with open(schema_file_path, "r", encoding="UTF-8") as file_instance:
        schema = json.load(file_instance)

    input_file_object = gear_context.get_input("input_file")
    if validation_level == "flywheel":
        strategy = "flywheel-file" if input_file_object else "flywheel-container"
    else:
        strategy = "local-file" if input_file_object else "INVALID"

    loader = loaders.FwLoader(
        context=gear_context,
        strategy=strategy,
        add_parents=add_parents,
        input_file_key="input_file",
    )
    input_json = loader.load()
    flywheel_hierarchy = loader.fw_meta_dict

    return (
        debug,
        tag,
        validation_level,
        schema,
        input_json,
        flywheel_hierarchy,
        strategy,
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
