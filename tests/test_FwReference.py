import os
from pathlib import Path

import flywheel
import flywheel_gear_toolkit
import pytest

from fw_gear_file_validator.utils import FwReference, PARENT_ORDER

config_file = "/Users/davidparker/Documents/Flywheel/SSE/MyWork/Gears/file-validator/file-validator/tests/assets/config.json"

client = flywheel.Client(os.environ["FWGA_API"])
context = flywheel_gear_toolkit.GearToolkitContext(
    config_path=config_file
)
context._client = client


def test_is_valid():
    with pytest.raises(ValueError):
        ref = FwReference(file_path=Path("does/not/exist.txt"))
    
    ref = FwReference(file_path=Path(config_file))
    assert ref.is_valid()
    
    with pytest.raises(ValueError):
        ref = FwReference(cont_type="none")

    for parent in PARENT_ORDER:
        ref = FwReference(cont_type=parent)
        assert ref.is_valid()

    
def test_loc():
    ref = FwReference(file_path=Path(config_file))
    assert ref.loc() == Path(config_file)

    ref = FwReference(cont_type="subject")
    assert ref.loc() == ref


def test_validate_file_contents():
    ref = FwReference(file_path=Path(config_file))
    assert ref.validate_file_contents()

    ref = FwReference(cont_type="subject")
    assert ref.validate_file_contents() is False


def test_client():
    ref = FwReference(file_path=Path(config_file))
    with pytest.raises(ValueError):
        ref.client

    ref = FwReference(file_path=Path(config_file), _client=client)
    assert ref.client == client


def test_container():

    ses_id = "63ceeda12bae5aafaf66306e"
    file_id = "6442edd40e732989de85e54d"
    file_name = "json_classifier.yaml"
    file_type = "json"

    ref = FwReference(cont_type="session",
                      cont_id=ses_id,
                      _client=client)

    ses = client.get_session(ses_id)
    assert ref.container.id == ses.id

    ref = FwReference(cont_type="session",
                      cont_id=ses_id,
                      _client=client,
                      file_name=file_name,
                      file_type=file_type)

    file = client.get_file(file_id)
    assert ref.container.file_id == file.file_id


def test_parents():
    ses_id = "63ceeda12bae5aafaf66306e"
    file_id = "6442edd40e732989de85e54d"
    file_name = "json_classifier.yaml"
    file_type = "json"

    ref = FwReference(cont_type="session",
                      cont_id=ses_id,
                      _client=client)

    ses = client.get_session(ses_id)
    parents = ref.parents
    print(parents)
    for parent in ses.parents.keys():
        print(parent)
        print(parents[parent].id)
        print(ses.parents[parent])
        assert parents[parent].id == ses.parents[parent]

    ref = FwReference(cont_type="session",
                      cont_id=ses_id,
                      _client=client,
                      file_name=file_name,
                      file_type=file_type)

    file = client.get_file(file_id)
    parents = ref.parents
    for parent in file.parents.keys():
        print(parent)
        if parent in parents:
            print(parents[parent].id)
            print(ref.parents[parent])
            assert parents[parent].id == file.parents[parent]


def test_all():
    acq_id = "63ceedbd866bff5a5fc6082e"
    file_id = "6442edd40e732989de85e54d"
    file_name = "test_json_form.json"
    wront_file_name = "nothere.txt"
    file_type = "json"

    ref = FwReference(cont_type="acquisition",
                      cont_id=acq_id,
                      _client=client)

    a = ref.all

    ref = FwReference(cont_type="acquisition",
                      cont_id=acq_id,
                      _client=client,
                      file_name=file_name,
                      file_type=file_type)

    b = ref.all

















