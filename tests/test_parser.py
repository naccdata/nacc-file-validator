"""Module to test parser.py"""
import os
from pathlib import Path

import flywheel
import pytest
from flywheel_gear_toolkit import GearToolkitContext

from fw_gear_file_validator import parser

# from fw_gear_{{gear_package}}.parser import parse_config
BASE_DIR = d = Path(__file__).resolve().parents[1]
BASE_DIR = BASE_DIR / "tests"
test_config = BASE_DIR / "assets" / "config.json"


def test_parse_config():
    """Here is an example of what you should add in your parse_config Testing
    gear_context = MagicMock(spec=GearToolkitContext)

    parse_config(gear_context)

    assert gear_context.get_input_path.call_count == 1
    assert gear_context.get_input.call_count == 0

    """

    context = GearToolkitContext(config_path=test_config)

    client = flywheel.Client(os.environ["FWGA_API"])
    context._client = client
    (
        debug,
        tag,
        schema_file_path,
        fw_reference,
        loader_config
    ) = parser.parse_config(context)
    assert fw_reference.is_file()

    assert loader_config["add_parents"] is False

    assert fw_reference.cont_id == "63bece9e873b883e03663191"
    assert fw_reference.cont_type == "acquisition"
    assert fw_reference.file_name == "test_input_valid.json"
    assert fw_reference.file_type == "json"

    assert tag == "file-validator"

    assert debug is False


def test_identify_file_type():
    file_str = "test_file_name.json"
    str_ext = parser.identify_file_type(file_str)
    assert str_ext == "json"

    file_path = Path(file_str)
    path_ext = parser.identify_file_type(file_path)
    assert path_ext == "json"

    context = GearToolkitContext(config_path=test_config)
    file_fw = context.get_input("input_file")
    fw_ext = parser.identify_file_type(file_fw)
    assert fw_ext == "json"

    file_fw["location"]["name"] = "noext"
    mime_ext = parser.identify_file_type(file_fw)
    assert mime_ext == "json"

    bad_str = "unsupported.ext"
    with pytest.raises(TypeError) as e_info:
        _ = parser.identify_file_type(bad_str)
