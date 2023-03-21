"""Parser module to parse gear config.json."""

import os
from pathlib import Path
from typing import Tuple, Union
from dataclasses import dataclass

from flywheel_gear_toolkit import GearToolkitContext

from fw_gear_file_validator.env import (
    SUPPORTED_FILE_EXTENSIONS,
    SUPPORTED_FLYWHEEL_MIMETYPES,
)

level_dict = {"Validate File Contents": "file", "Validate Flywheel Objects": "flywheel"}


@dataclass
class FwReference:
    dest_id: str = None
    dest_type: str = None
    file_id: str = None
    file_name: str = None
    file_type: str = None

    @property
    def is_file(self):
        return self.file_id is not None


# This function mainly parses gear_context's config.json file and returns relevant
# inputs and options.
def parse_config(
        gear_context: GearToolkitContext,
) -> Tuple[bool, str, str, str, Path, FwReference]:
    """parses necessary items out of the context object"""

    debug = gear_context.config.get("debug")
    tag = gear_context.config.get("tag", "file-validator")
    add_parents = gear_context.config.get("add_parents")
    validation_level = gear_context.config.get("validation_level")
    validation_level = level_dict[validation_level]
    schema_file_path = Path(gear_context.get_input_path("validation_schema"))

    local_file_object = gear_context.get_input("input_file")
    local_file_type = identify_file_type(local_file_object)

    fw_reference = FwReference()
    fw_reference.dest_id = gear_context.destination["id"]
    fw_reference.dest_type = gear_context.destination["type"]
    fw_reference.file_id = local_file_object.get("object", {}).get("file_id")
    fw_reference.file_name = local_file_object.get("location", {}).get("name")
    fw_reference.file_type = local_file_type

    return (
        debug,
        tag,
        validation_level,
        add_parents,
        schema_file_path,
        fw_reference,
    )


def identify_file_type(input_file: Union[dict, str, Path]) -> str:
    """Given a flywheel config input file object, identify the file type."""
    ext = None
    mime = None
    input_file_type = None
    # see if the input file object has a value
    if not input_file:
        return ""
    # If it's a string make it a path
    if isinstance(input_file, str):
        input_file = Path(input_file)
    # If it's a path try to get the extension from the suffix
    if isinstance(input_file, Path):
        ext = input_file.suffix
    elif isinstance(input_file, dict):
        # First try to just check the file type from the file extension:
        file_name = input_file.get("location", {}).get("name")
        base, ext = os.path.splitext(file_name)
        mime = input_file["object"]["mimetype"]

    # If we managed to get an extension, that means that
    if ext:
        input_file_type = SUPPORTED_FILE_EXTENSIONS.get(ext)
    elif mime:
        input_file_type = SUPPORTED_FLYWHEEL_MIMETYPES.get(mime)
    if input_file_type is None:
        raise TypeError(f"file type {mime} is not supported")

    return input_file_type
