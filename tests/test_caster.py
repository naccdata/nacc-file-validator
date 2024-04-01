from fw_gear_file_validator import utils
import pytest

JSON_TYPES = {"string": str, "number": float, "integer": int, "boolean": bool, "null": utils.null}

def test_cast_one_valid():
    cast_type = int
    value = "123"
    new_value = utils.cast_one(value, cast_type)
    assert new_value == int(value)

def test_cast_one_invalid():
    cast_type = int
    value = "123.456"
    new_value = utils.cast_one(value, cast_type)
    assert new_value == value

def test_cast_types_single_valid():
    cast_type = [int]
    value = "123"
    new_value = utils.cast_csv_val(value, cast_type)
    assert new_value == int(value)

def test_cast_types_single_invalid():
    cast_type = [int]
    value = "123.456"
    new_value = utils.cast_csv_val(value, cast_type)
    assert new_value == value

def test_cast_types_single():
    cast_type = [int]
    value = "123"
    new_value = utils.cast_csv_val(value, cast_type)
    assert new_value == int(value)

def test_cast_null_valid():
    cast_type = [utils.null, str]
    value = ''
    new_value = utils.cast_csv_val(value, cast_type)
    assert new_value is None

def test_cast_null_invalid():
    cast_type = [utils.null, str]
    value = 'abc'
    new_value = utils.cast_csv_val(value, cast_type)
    assert new_value == value

def test_cast_multiple_invalid():
    cast_type = [int, str]
    value = '123'
    with pytest.raises(ValueError):
        new_value = utils.cast_csv_val(value, cast_type)

    cast_type = [int, str]
    value = 123
    with pytest.raises(ValueError):
        new_value = utils.cast_csv_val(value, cast_type)

def test_cast_multiple_valid():

    cast_type = [int, str]
    value = 'abc'
    new_value = utils.cast_csv_val(value, cast_type)
    assert new_value == value


