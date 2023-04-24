from flywheel import Acquisition, FileEntry, Group, Project, Session, Subject

from fw_gear_file_validator import utils


def test_get_lookup_path():
    fw_ref = utils.FwReference(
        cont_id="test_container_id",
        cont_type="acquisition",
        file_name="test_file_name.ext",
        file_path=None,
        file_type="test_file_type",
        _client=None,
    )

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
    file = FileEntry()
    file.name = "test_file_name.ext"

    parent_dict = {
        "group": group,
        "project": project,
        "subject": subject,
        "session": session,
        "acquisition": acquisition,
        "file": file,
    }

    fw_ref.__dict__["container"] = file
    fw_ref.__dict__["parents"] = parent_dict

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
