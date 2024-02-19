from fw_gear_file_validator import validator
from pathlib import Path
import json
import pandas as pd


# from fw_gear_{{gear_package}}.parser import parse_config
BASE_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = BASE_DIR / "tests"
test_config = BASE_DIR / "assets" / "config_csv.json"

with open(test_config) as f:
    CONFIG_JSON = json.load(f)
CONFIG_JSON["inputs"]["input_file"]["location"]["path"] = BASE_DIR / "assets" / CONFIG_JSON["inputs"]["input_file"]["location"]["name"]
CONFIG_JSON["inputs"]["validation_schema"]["location"]["path"] = BASE_DIR / "assets" / CONFIG_JSON["inputs"]["validation_schema"]["location"]["name"]


def test_validate_csv():

    csv_path = CONFIG_JSON["inputs"]["input_file"]["location"]["path"]
    csv_table = pd.read_csv(csv_path)
    schema_path = CONFIG_JSON["inputs"]["validation_schema"]["location"]["path"]
    csv_validator = validator.CsvValidator(schema_path)
    valid, errors = csv_validator.validate(csv_table)

    assert not valid
    assert len(errors) == 1

    csv_table["Col2"][1] = 2
    valid, errors = csv_validator.validate(csv_table)
    assert valid
    assert errors == []



