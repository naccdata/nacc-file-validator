import os
from pathlib import Path

import flywheel
import flywheel_gear_toolkit

import fw_gear_file_validator
from fw_gear_file_validator.loader import FwLoader
from fw_gear_file_validator.utils import FwReference

client = flywheel.Client(os.environ["FWGA_API"])
BASE_DIR = d = Path(__file__).resolve().parents[1]
BASE_DIR = BASE_DIR / "tests"
test_config = BASE_DIR / "assets" / "config.json"
context = flywheel_gear_toolkit.GearToolkitContext(config_path=test_config)
context._client = client


def test_loader_init():
    fw_reference = FwReference(
        cont_id=context.destination["id"],
        cont_type=context.destination["type"],
        file_name=context.get_input_filename("input_file"),
        file_path=None,
        file_type="json",
        _client=context.client,
    )

    config = {"add_parents": True}
    loader = FwLoader(config=config)
    validation_dict = loader.load_object(fw_reference)

    assert "file" in validation_dict
    assert "project" in validation_dict
    assert "subject" in validation_dict
    assert "session" in validation_dict
    assert "acquisition" in validation_dict
    assert "analysis" not in validation_dict

    config = {"add_parents": False}
    loader = FwLoader(config=config)
    validation_dict = loader.load_object(fw_reference)

    assert "file" in validation_dict
    assert "project" not in validation_dict
    assert "subject" not in validation_dict
    assert "session" not in validation_dict
    assert "acquisition" not in validation_dict
    assert "analysis" not in validation_dict
