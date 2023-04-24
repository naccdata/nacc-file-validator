import tempfile
from pathlib import Path

from fw_gear_file_validator import errors

BASE_DIR = d = Path(__file__).resolve().parents[1]
test_config = BASE_DIR / "tests" / "assets" / "config.json"


def test_save_errors():
    error_dict = [{"key1": "k1v1", "key2": "k2v1"}, {"key1": "k1v2", "key2": "k2v2"}]
    filename = "errors.csv"
    with tempfile.TemporaryDirectory() as output_dir:
        errors.save_errors(error_dict, output_dir, filename)
        file_out = Path(output_dir) / filename
        assert file_out.exists()
