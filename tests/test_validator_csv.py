import csv
import json
from pathlib import Path

from fw_gear_file_validator import validator

# from fw_gear_{{gear_package}}.parser import parse_config
BASE_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = BASE_DIR / "tests"
test_config = BASE_DIR / "assets" / "config_csv.json"

with open(test_config) as f:
    CONFIG_JSON = json.load(f)

CONFIG_JSON["inputs"]["validation_schema"]["location"]["path"] = (
    BASE_DIR / "assets" / CONFIG_JSON["inputs"]["validation_schema"]["location"]["name"]
)


def set_csv_path(csv_name):
    CONFIG_JSON["inputs"]["input_file"]["location"]["path"] = (
        BASE_DIR / "assets" / csv_name
    )


def test_validate_csv():
    set_csv_path("test_input_valid.csv")
    csv_path = CONFIG_JSON["inputs"]["input_file"]["location"]["path"]
    schema_path = CONFIG_JSON["inputs"]["validation_schema"]["location"]["path"]
    csv_validator = validator.CsvValidator(schema_path)
    with open(csv_path) as csv_file:
        csv_table = list(csv.DictReader(csv_file))
        valid, errors = csv_validator.validate(csv_table)

    assert valid
    assert len(errors) == 0

    set_csv_path("test_input_invalid.csv")
    csv_path = CONFIG_JSON["inputs"]["input_file"]["location"]["path"]
    with open(csv_path) as csv_file:
        csv_table = list(csv.DictReader(csv_file))
        valid, errors = csv_validator.validate(csv_table)
    assert not valid
    assert len(errors) == 1


def test_empty_csv():
    schema = {"properties": {"list": {"type": "array", "maxItems": 3}, "num": {"type": "number"}}}
    cvalidator = validator.CsvValidator(schema)
    valid, errors = cvalidator.validate([])
    assert valid is False
    assert len(errors) == 1
    assert errors[0]["code"] == "EmptyFile"


def test_no_header_csv():
    schema = {"properties": {"list": {"type": "array", "maxItems": 3}, "num": {"type": "number"}}}
    cvalidator = validator.CsvValidator(schema)
    valid, errors = cvalidator.validate([{"a": "as", "b": "bs"}])
    assert valid is False
    assert len(errors) == 1
    assert errors[0]["code"] == "MissingHeader"


def test_incorrect_header_csv():
    schema = {"properties": {"list": {"type": "array", "maxItems": 3}, "num": {"type": "number"}}}
    cvalidator = validator.CsvValidator(schema)
    valid, errors = cvalidator.validate([{"list": "as", "b": "bs"}])
    assert valid is False
    assert len(errors) == 1
    assert errors[0]["code"] == "IncorrectColumnName"

