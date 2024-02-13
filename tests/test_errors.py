import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import flywheel
from fw_gear_file_validator import errors
from fw_gear_file_validator import utils

BASE_DIR = d = Path(__file__).resolve().parents[1]
test_config = BASE_DIR / "tests" / "assets" / "config.json"


def test_save_errors_csv():
    error_dict = [{"key1": "k1v1", "key2": "k2v1"}, {"key1": "k1v2", "key2": "k2v2"}]
    filename = "errors.csv"
    with tempfile.TemporaryDirectory() as output_dir:
        errors.save_errors_csv(error_dict, output_dir, filename)
        file_out = Path(output_dir) / filename
        assert file_out.exists()

def test_save_errors_metadata():
    error_dict = [{"key1": "k1v1", "key2": "k2v1"}, {"key1": "k1v2", "key2": "k2v2"}]
    context = MagicMock()
    file_name = "test_file_name.ext"
    file_id = "test_container_id"
    file_type = "test_file_type"
    parent_dict = {}

    file = flywheel.FileEntry(name=file_name,
                     file_id=file_id,
                     type=file_type,
                     parents=parent_dict)
    fw_ref = utils.FwReference.init_from_object(None, file)

    errors.save_errors_metadata(error_dict, fw_ref, context)
    context.metadata.add_qc_result.assert_called_with(file_name, "validation", state="FAIL", data={"data":error_dict})