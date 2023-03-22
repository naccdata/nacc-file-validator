import os

import flywheel
import flywheel_gear_toolkit

import fw_gear_file_validator.flywheel_utils.flywheel_loaders
from fw_gear_file_validator.flywheel_utils.flywheel_env import (
    FwLoaderConfig,
    FwReference,
)

client = flywheel.Client(os.environ["FWGA_API"])
context = flywheel_gear_toolkit.GearToolkitContext(
    config_path="/Users/davidparker/Documents/Flywheel/SSE/MyWork/Gears/file-validator/file-validator/tests/assets/config.json"
)
context._client = client


def test_loader_init():
    config = FwLoaderConfig(add_parents=False, validation_level="file")
    fw_reference = FwReference
    fw_reference.file_name = context.get_input_filename("input_file")
    fw_reference.file_id = context.get_input_file_object_value("input_file", "file_id")
    fw_reference.dest_type = context.destination["type"]
    fw_reference.dest_id = context.destination["id"]
    fw_reference.file_type = "json"
    fw_reference.input_name = "input_file"

    print(fw_reference.file_name)
    loader = fw_gear_file_validator.flywheel_utils.flywheel_loaders.FwLoader(
        context=context, config=config
    )

    full_fw_meta, validation_dict = loader.load(fw_reference)

    assert "file" not in validation_dict

    config = FwLoaderConfig(add_parents=True, validation_level="file")

    loader = fw_gear_file_validator.flywheel_utils.flywheel_loaders.FwLoader(
        context=context, config=config
    )

    full_fw_meta, validation_dict = loader.load(fw_reference)
    assert "file" in validation_dict
