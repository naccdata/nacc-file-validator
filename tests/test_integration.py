import os
from pathlib import Path

import flywheel
import flywheel_gear_toolkit

import run

BASE_DIR = d = Path(__file__).resolve().parents[1]
manifest_path = BASE_DIR / "manifest.json"
BASE_DIR = BASE_DIR / "tests"
test_config = BASE_DIR / "assets" / "integration_config.json"


def test_integration():
    if "FWGA_API" not in os.environ:
        assert True
        return

    print(BASE_DIR)
    context = flywheel_gear_toolkit.GearToolkitContext(
        manifest_path=manifest_path, config_path=test_config
    )
    client = flywheel.Client(os.environ["FWGA_API"])
    context._client = client
    run.main(context)
