
import flywheel_gear_toolkit
import os
import flywheel
from pathlib import Path
import run

BASE_DIR = d = Path(__file__).resolve().parents[2]
BASE_DIR = BASE_DIR / "tests" / "integration"
#BASE_DIR="/Users/davidparker/Documents/Flywheel/SSE/MyWork/Gears/file-validator/tests/integration"
def test_integration():
    print(BASE_DIR)
    context = flywheel_gear_toolkit.GearToolkitContext(gear_path=BASE_DIR)
    run.main(context)
    assert False