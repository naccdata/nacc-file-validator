"""Parser module to parse gear config.json."""

import logging
import os
import typing as t
import flywheel
from pathlib import Path
import json

import flywheel_gear_toolkit.context
from flywheel_gear_toolkit import GearToolkitContext
from env import SUPPORTED_FILE_EXTENSIONS, SUPPORTED_FLYWHEEL_MIMETYPES


# This function mainly parses gear_context's config.json file and returns relevant
# inputs and options.
def parse_config(
    gear_context: GearToolkitContext,
) -> t.Tuple[bool, bool, str, dict, str, dict]:
    """[Summary]

    Returns:
        [type]: [description]
    """

    debug = gear_context.config.get("debug")
    tag = gear_context.config.get("tag", "file-validator")
    schema_file_object = gear_context.get_input("validation_schema")
    schema_file_type = identify_file_type(schema_file_object)
    schema_file_path = schema_file_object["location"]["path"]

    input_file_object = gear_context.get_input("input_file")
    input_file_path = input_file_object["location"]["path"]
    validate_metadata = gear_context.config.get("validate_metadata")
    if validate_metadata:
        input_file_path = save_metadata_to_file(gear_context.client, input_file_object)

    return debug, tag, schema_file_path, schema_file_type, input_file_object, input_file_path


def identify_file_type(input_file: dict) -> str:
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


def save_metadata_to_file(context: flywheel_gear_toolkit.context.GearToolkitContext, gear_file_object: t.Dict) -> Path:
    file_id = gear_file_object['object']['file_id']
    flywheel_file = context.client.get_file(file_id)
    file_out = context.work_dir / "fw_file_object.json"
    # Possible data type loss here with default set to str
    file_str = json.dumps(flywheel_file.to_dict(), indent=4, sort_keys=True, default=str)
    with open(file_out, 'w') as json_out:
        json_out.write(file_str)

    return file_out