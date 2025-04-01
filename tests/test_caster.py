from fw_gear_file_validator import utils

JSON_TYPES = {"string": str, "number": float, "integer": int, "boolean": bool}


def test_cast_one_valid():
    cast_type = int
    value = "123"
    new_value = utils.cast_value(value, cast_type)
    assert new_value == int(value)


def test_cast_one_invalid():
    cast_type = int
    value = "123.456"
    new_value = utils.cast_value(value, cast_type)
    assert new_value == value
