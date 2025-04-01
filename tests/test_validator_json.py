from fw_gear_file_validator import validator


def test_process_json():
    schema = {"properties": {"list": {"type": "array", "maxItems": 3}}}
    json_object = {"list": [1, 2, 3]}
    jvalidator = validator.JsonValidator(schema)
    valid, errors = jvalidator.process_item(json_object)
    assert valid
    assert errors == []

    json_object = {"list": [1, 2, 3, 4]}
    jvalidator = validator.JsonValidator(schema)
    valid, errors = jvalidator.process_item(json_object)
    assert not valid
    assert len(errors) == 1
    print(errors)


def test_validate_json():
    # Note presently this test is identical to test_process, except we
    # call validate
    schema = {"properties": {"list": {"type": "array", "maxItems": 3}}}
    json_object = {"list": [1, 2, 3]}
    jvalidator = validator.JsonValidator(schema)
    valid, errors = jvalidator.validate(json_object)
    assert valid
    assert errors == []

    json_object = {"list": [1, 2, 3, 4]}
    jvalidator = validator.JsonValidator(schema)
    valid, errors = jvalidator.validate(json_object)
    assert not valid
    assert len(errors) == 1


def test_handle_errors_json():
    schema = {"properties": {"list": {"type": "array", "maxItems": 3}}}
    json_object = {"list": [1, 2, 3, 4]}
    jvalidator = validator.JsonValidator(schema)
    errors = jvalidator.validator.iter_errors(json_object)
    packaged_errors = jvalidator.handle_errors(errors)
    packaged_error = packaged_errors[0]
    print(packaged_error["value"])

    assert packaged_error["type"] == "error"
    assert packaged_error["location"] == {"key_path": "properties.list"}
    assert packaged_error["expected"] == "{'type': 'array', 'maxItems': 3}"
    assert packaged_error["message"] == "[1, 2, 3, 4] is too long"
    assert packaged_error["code"] == "maxItems"
    assert packaged_error["value"] == "[1, 2, 3, 4]"


def test_empty_json():
    schema = {"properties": {"list": {"type": "array", "maxItems": 3}}}
    jvalidator = validator.JsonValidator(schema)
    valid, errors = jvalidator.validate({})
    assert valid is False
    assert len(errors) == 1
    assert errors[0]["code"] == "empty-file"


def test_cast_json():
    schema =  {"properties": {"num_value": {"type": "number"}}}
    jvalidator = validator.JsonValidator(schema)
    valid, errors = jvalidator.validate({"num_value": 1})
    assert valid

    valid, errors = jvalidator.validate({"num_value": 1.0})
    assert valid

    valid, errors = jvalidator.validate({"num_value": "1.0"})
    assert valid
