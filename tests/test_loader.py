import io
import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from fw_gear_file_validator.loader import CsvLoader, FwLoader, JsonLoader
from fw_gear_file_validator.utils import FwReference

BASE_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = BASE_DIR / "tests"
test_config = BASE_DIR / "assets" / "config.json"

with open(test_config) as f:
    CONFIG_JSON = json.load(f)

CONFIG_JSON["inputs"]["input_file"]["location"]["path"] = (
    BASE_DIR / "assets" / CONFIG_JSON["inputs"]["input_file"]["location"]["name"]
)


def context_get_input_path_side_effect(value):
    return BASE_DIR / "assets" / CONFIG_JSON["inputs"][value]["location"]["name"]


def context_get_input_filename_side_effect(value):
    return CONFIG_JSON["inputs"][value]["location"]["name"]


def context_get_input_side_effect(value):
    return CONFIG_JSON["inputs"][value]


def test_loader_init():
    context = MagicMock()
    context.get_input_path.side_effect = context_get_input_path_side_effect
    context.get_input_filename.side_effect = context_get_input_filename_side_effect
    context.get_input.side_effect = context_get_input_side_effect
    context.config = CONFIG_JSON["config"]
    context.destination = CONFIG_JSON["destination"]

    client = MagicMock()
    context._client = client

    fw_reference = FwReference.init_from_gear_input(
        client, context.get_input("input_file"), "flywheel"
    )
    fw_reference.parents = {"acquisition": "1234"}
    fw_reference.__post_init__()
    config = {"add_parents": True}
    loader = FwLoader(config=config)
    validation_dict, errors = loader.load_object(fw_reference.loc)

    client.get_file.assert_called()
    client.get_file().parents.keys.assert_called()
    client.get_acquisition.assert_called()
    assert validation_dict == {"acquisition": {}, "file": {}}
    assert errors is None

    client2 = MagicMock()
    fw_reference = FwReference.init_from_gear_input(
        client2, context.get_input("input_file"), "flywheel"
    )
    fw_reference.parents = {"acquisition": "1234"}
    fw_reference.__post_init__()

    config = {"add_parents": False}
    loader = FwLoader(config=config)
    validation_dict = loader.load_object(fw_reference.loc)

    client2.get_file.assert_called()


def test_load_empty_json():
    loader = JsonLoader()
    with tempfile.NamedTemporaryFile() as fp:
        # create an empty file
        fp.write(b"")
        fp.seek(0)
        file_object, errors = loader.load_object(Path(fp.name))
    assert file_object is None
    assert errors[0]["message"] == "The File Is Empty"


def test_load_empty_csv():
    loader = CsvLoader()
    with tempfile.NamedTemporaryFile() as fp:
        # create an empty file
        fp.write(b"")
        fp.seek(0)
        file_object, _errors = loader.load_object(Path(fp.name))
    assert file_object is None


def test_validate_file_format_valid():
    mock_file = MagicMock()
    mock_file.__iter__.return_value = iter(
        ["header1,header2,header3\n", "value1,value2,value3\n"]
    )
    with patch("fw_gear_file_validator.loader.open", return_value=mock_file):
        loader = CsvLoader()
        result = loader.validate_file_format(Path("dummy_path.csv"))
        assert result is None


def test_validate_file_format_syntax_error():
    mock_return_value = io.StringIO("header1,header2,header3\nvalue1,value2\n")
    with patch("fw_gear_file_validator.loader.open", return_value=mock_return_value):
        loader = CsvLoader()
        result = loader.validate_file_format(Path("dummy_path.csv"))
        assert result is not None


def test_validate_num_commas_valid():
    mock_file = io.StringIO("header1,header2,header3\nvalue1,value2,value3\n")
    result = CsvLoader.validate_num_commas(mock_file)
    assert result is None


def test_validate_num_commas_with_quotes():
    # Test CSV with quoted fields containing commas
    mock_file = io.StringIO(
        'header1,header2,header3\nvalue1,"value2,with,commas",value3\n'
    )
    result = CsvLoader.validate_num_commas(mock_file)
    assert result is None


def test_validate_num_commas_with_quotes_error():
    # Test CSV with incorrect number of fields, even with quotes
    mock_file = io.StringIO('header1,header2,header3\nvalue1,"value2,with,commas"\n')
    result = CsvLoader.validate_num_commas(mock_file)
    assert result is not None
    assert "Row 2 has 2 fields while the header has 3 fields" in result.message


def test_validate_num_commas_with_invalid_quotes():
    # Test CSV with incorrectly quoted fields
    mock_file = io.StringIO(
        'header1,header2,header3\nvalue1,"value2,with,unclosed quote,value3\n'
    )
    result = CsvLoader.validate_num_commas(mock_file)
    assert result is not None
    assert "CSV parsing error" in result.message


def test_validate_file_header_valid():
    mock_file = io.StringIO("header1,header2,header3\n")
    result = CsvLoader.validate_file_header(mock_file)
    assert result is None


def test_validate_file_header_empty():
    mock_file = io.StringIO("\n")
    result = CsvLoader.validate_file_header(mock_file)
    assert result is not None


def test_validate_file_header_duplicate():
    mock_file = io.StringIO("header1,header2,header2\n")
    result = CsvLoader.validate_file_header(mock_file)
    assert result is not None
