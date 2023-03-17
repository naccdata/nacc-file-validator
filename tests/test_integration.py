
import flywheel_gear_toolkit
import os
import flywheel
from pathlib import Path
import run

BASE_DIR = d = Path(__file__).resolve().parents[1]
BASE_DIR = BASE_DIR / "tests"
test_config = BASE_DIR / "assets" / "config.json"

#BASE_DIR="/Users/davidparker/Documents/Flywheel/SSE/MyWork/Gears/file-validator/tests/integration"
def test_integration():
    print(BASE_DIR)
    context = flywheel_gear_toolkit.GearToolkitContext(config_path=test_config)
    client = flywheel.Client(os.environ["FWGA_API"])
    context._client = client
    run.main(context)
