"""Module to test parser.py"""
from pathlib import Path
from flywheel_gear_toolkit import GearToolkitContext
import flywheel
import os

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
        validation_level,
        schema_file_path,
        input_json,
        flywheel_hierarchy,
        strategy,
    ) = parser.parse_config(context)

    assert validation_level == "file"
    assert strategy == "local-file"

