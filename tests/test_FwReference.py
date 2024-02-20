from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from flywheel import Acquisition, FileEntry, Group, Project, Session, Subject

from fw_gear_file_validator import utils

PARENT_ORDER = utils.PARENT_ORDER
FwReference = utils.FwReference

BASE_DIR = d = Path(__file__).resolve().parents[1]
BASE_DIR = BASE_DIR / "tests"
test_config = BASE_DIR / "assets" / "config.json"


def test_is_valid():
    with pytest.raises(ValueError):
        ref = FwReference(type="file", parents={})
        ref.file_path = Path("does/not/exist.txt")
        ref.path_is_valid()

    ref = FwReference(type="file", parents={})
    ref.file_path = Path(test_config)
    assert ref.path_is_valid()

    with pytest.raises(ValueError):
        _ = FwReference(type="none", parents={})

    for parent in PARENT_ORDER:
        ref = FwReference(type=parent, parents={})
        assert ref.path_is_valid()




def test_parents():
    ses_id = "63ceeda12bae5aafaf66306e"
    ses_label = "test_ses"
    client = MagicMock()
    parents = {
        "group": "gid",
        "project": "pid",
        "subject": "sid",
        "session": None,
        "acquisition": None,
    }
    session = Session(id=ses_id, label=ses_label, parents=parents)


    ref = FwReference.init_from_object(client, session)
    _ = ref.fw_object()

    client.get_session.assert_called_once()
    client.get_session().get_file.assert_not_called()

    client = MagicMock()
    parents = {"session":ses_id}
    file_id = "6442edd40e732989de85e54d"
    file_name = "json_classifier.yaml"
    file_type = "json"


    file = FileEntry(name=file_name,
                     file_id=file_id,
                     type=file_type,
                     parents=parents)

    ref = FwReference.init_from_object(client, file)
    _ = ref.hierarchy_objects
    client.get_file.assert_called_once()
    client.get_session.assert_called_once()


def test_get_lookup_path():

    group = Group()
    group.label = "test_group"
    project = Project()
    project.label = "test_project"
    subject = Subject()
    subject.label = "test_subject"
    session = Session()
    session.label = "test_session"
    acquisition = Acquisition()
    acquisition.label = "test_acquisition"
    file_name = "test_file_name.ext"
    file_id = "test_container_id"
    file_type = "test_file_type"
    parent_dict = {
        "group": group,
        "project": project,
        "subject": subject,
        "session": session,
        "acquisition": acquisition,
    }

    file = FileEntry(name=file_name,
                     file_id=file_id,
                     type=file_type,
                     parents=parent_dict)
    object_hierarchy = {
        "group": group,
        "project": project,
        "subject": subject,
        "session": session,
        "acquisition": acquisition,
        "file": file
    }

    fw_ref = FwReference.init_from_object(None, file)
    fw_ref.hierarchy_objects = object_hierarchy
    url = f"fw://{group.label}/{project.label}/{subject.label}/{session.label}/{acquisition.label}/{file.name}"
    assert fw_ref.get_lookup_path() == url

    url = f"fw://{group.label}/{project.label}/{subject.label}/{session.label}/{acquisition.label}"
    assert fw_ref.get_lookup_path(level="acquisition") == url

    url = f"fw://{group.label}/{project.label}/{subject.label}/{session.label}"
    assert fw_ref.get_lookup_path(level="session") == url

    url = f"fw://{group.label}/{project.label}/{subject.label}"
    assert fw_ref.get_lookup_path(level="subject") == url

    url = f"fw://{group.label}/{project.label}"
    assert fw_ref.get_lookup_path(level="project") == url

    url = f"fw://{group.label}"
    assert fw_ref.get_lookup_path(level="group") == url


def test_container_retrys():
    utils.SLEEP_TIME = 0.1

    my_client = MagicMock()
    my_client.get_file = MagicMock(return_value=None)
    file_name = "test_file_name.ext"
    file_id = "test_container_id"
    file_type = "test_file_type"
    parents = {}

    file = FileEntry(name=file_name,
                   file_id=file_id,
                   type=file_type,
                   parents=parents)

    fw_ref = FwReference.init_from_object(my_client, file)

    with pytest.raises(ValueError) as e_info:
        fw_ref.fw_object

    assert my_client.get_file.call_count == utils.N_TRIES


def test_parent_retrys():
    utils.SLEEP_TIME = 0.1

    session_label = "test_session"
    my_client = MagicMock()
    session = Session()
    session.label = session_label
    session.parents = {
        "group": "gid",
        "project": "pid",
        "subject": "sid",
        "session": None,
        "acquisition": None,
    }

    my_client.get_session = MagicMock(return_value=session)
    my_client.get_subject = MagicMock(return_value=None)
    my_client.get_project = MagicMock(return_value=None)
    my_client.get_group = MagicMock(return_value=None)

    fw_ref = FwReference(
        id="test_container_id",
        type="session",
        name=session_label,
        is_file=False,
        _client=my_client,
        input_object=session,
        parents=session.parents
    )

    with pytest.raises(ValueError) as e_info:
        fw_ref.hierarchy_objects

    assert my_client.get_group.call_count == utils.N_TRIES
