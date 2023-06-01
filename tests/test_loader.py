import os
from pathlib import Path
from unittest.mock import MagicMock

import flywheel
import flywheel_gear_toolkit

import fw_gear_file_validator
from fw_gear_file_validator.loader import FwLoader
from fw_gear_file_validator.utils import FwReference

BASE_DIR = d = Path(__file__).resolve().parents[1]
BASE_DIR = BASE_DIR / "tests"
test_config = BASE_DIR / "assets" / "config.json"


def test_loader_init():
    context = flywheel_gear_toolkit.GearToolkitContext(config_path=test_config)
    client = MagicMock()
    context._client = client


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

    client.get_acquisition().get_file.assert_called_once()
    client.get_acquisition().get_file().parents.items.assert_called_once()

    client = MagicMock()
    fw_reference = FwReference(
        cont_id=context.destination["id"],
        cont_type=context.destination["type"],
        file_name=context.get_input_filename("input_file"),
        file_path=None,
        file_type="json",
        _client=client,
    )

    config = {"add_parents": False}
    loader = FwLoader(config=config)
    validation_dict = loader.load_object(fw_reference)

    client.get_acquisition().get_file.assert_called_once()
    client.get_acquisition().get_file().parents.items.assert_not_called()

