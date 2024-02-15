import logging
import time
import typing as t
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

import flywheel
import flywheel_gear_toolkit
from flywheel_gear_toolkit.utils.datatypes import Container

PARENT_ORDER = [
    "group",
    "project",
    "subject",
    "session",
    "acquisition",
    "analysis",
    "file",
]

log = logging.getLogger()

N_TRIES = 5
SLEEP_TIME = 5


@dataclass
class FwReference:
    """A reference to a flywheel object (being a container or a gear input file).

    Host a set of methods to facilitate the loading of the object in its specific
    context (gear input file, flywheel container or flywheel file).

    Attributes:
        id: str, the id of the container
        object: flywheel object, the flywheel object
        type: str, the type of the container
        parents: dict, the parents of the container
        name: str, the name of the container
        is_file: bool, True if the object is a file, False otherwise
        ref: dict, the reference to the object, basically the parent dictionary plus the object itself.
        _client: flywheel.Client, the flywheel client

    Properties (cached):
        parent_type: str, container type of the object's parent
        parent_id: str: The container ID of the object's parent
        my_object: the full flywheel object.


    """

    id: str = None
    input_object: t.Union[flywheel.ContainerReference, flywheel.FileReference, flywheel.JobFileInput, flywheel.JobFileInput, dict] = None
    type: str = None
    parents: dict = None
    name: str = None
    is_file: bool = False
    file_type: str = None
    ref: dict = None
    _client: flywheel.Client = None


    @classmethod
    def init_from_object(cls, fw_client, fw_object):
        """Initializes a FwReference object from a flywheel object."""
        if cls._object_is_file(fw_object):
            return cls.init_from_file(fw_client, fw_object)
        return cls.init_from_container(fw_client, fw_object)

    @classmethod
    def init_from_file(cls, fw_client, fw_object):
        if "location" in fw_object:
            file_object = fw_object["object"]
        else:
            file_object = fw_object
        if 'parents' not in file_object:
            file_object = fw_client.get_file(file_object["file_id"])
        return cls(
            input_object=fw_object,
            id=file_object["file_id"],
            type="file",
            name=file_object.name,
            is_file=True,
            file_type=file_object.type,
            _client=fw_client,
            parents=dict(file_object.parents),
        )

    @classmethod
    def init_from_container(cls, fw_client, fw_object):
        return cls(
            id=fw_object.id,
            type=fw_object.container_type,
            name=fw_object.label,
            _client=fw_client,
            parents=dict(fw_object.parents),
            input_object=fw_object
        )

    @staticmethod
    def _object_is_file(fw_object):
        if isinstance(fw_object, flywheel.FileEntry) or "mimetype" in fw_object or "location" in fw_object:
            return True
        return False

    def __post_init__(self):
        self.is_valid()
        self.parents = {k: v for k, v in self.parents.items() if v} # remove None's
        self.ref = {**self.parents, self.type: self.id}


    def is_valid(self) -> bool:
        """Returns True if the reference is valid, raise exception otherwise."""
        if self.file_path and not self.file_path.exists():
            raise ValueError(f"File {self.file_path} does not exist")
        if self.type and self.type not in PARENT_ORDER:
            raise ValueError(f"Invalid type {self.type}")
        return True

    #USED
    @cached_property
    def file_path(self):
        if self.input_object and "location" in self.input_object:
            path = Path(self.input_object["location"]["path"])
        else:
            path = None
        return path

    @cached_property
    def parent_type(self):
        """Returns the type of the parent."""
        for p in PARENT_ORDER[::-1]:
            if p in self.parents and self.parents[p] is not None:
                return p

    @cached_property
    def parent_id(self):
        """Returns the type of the parent."""
        for p in PARENT_ORDER[::-1]:
            if p in self.parents and self.parents[p] is not None:
                return self.parents[p]
    @property
    def loc(self) -> t.Union[Path, "FwReference"]:
        """Returns location of the object."""
        if self.file_path:
            return self.file_path
        else:
            return self.ref

    @property
    def client(self) -> flywheel.Client:
        """Returns the Flywheel client."""
        if not self._client:
            raise ValueError("Client not set. Use set_client() to set the client.")
        return self._client

    def set_client(self, client: flywheel.Client):
        """Sets the Flywheel client as attribute."""
        self._client = client

    #USED
    def get_lookup_path(self, level: str = None) -> str:
        """Returns the Flywheel path of the Flywheel object."""
        hierarchy_parts = []
        for k in PARENT_ORDER:
            if k in self.hierarchy_objects:
                if k == "file":
                    hierarchy_parts.append(self.hierarchy_objects[k].get("name"))
                else:
                    hierarchy_parts.append(self.hierarchy_objects[k].get("label"))
            if k == level:
                break
        return "fw://" + "/".join(hierarchy_parts)

    #USED
    @cached_property
    def fw_object(self) -> Container:
        """Returns the container for the provided Flywheel reference."""
        return self.get_level_object(self.type)

    #USED
    @cached_property
    def hierarchy_objects(self):
        hierarchy = {}
        for level, id in self.ref.items():
            fw_object = self.get_level_object(level)
            if fw_object is None:
                continue
            hierarchy[level] = fw_object
        return hierarchy

    #USED
    def get_level_object(self, level) -> t.Union[dict,None]:
        """Returns all the parent containers."""
        if level not in self.ref.keys():
            return None

        p_id = self.ref[level]
        getter = getattr(self.client, f"get_{level}")
        tries = 0
        while tries < N_TRIES:
            fw_object = getter(p_id)
            if fw_object:
                break
            tries += 1
            time.sleep(SLEEP_TIME)

        if not fw_object:
            # Better to exit here with a good error than crash later
            raise ValueError(f"Unable to retrieve object {level}: {p_id}")

        return fw_object



def add_tags_metadata(
    context: flywheel_gear_toolkit.GearToolkitContext,
    fw_ref: FwReference,
    valid,
    tag,
):
    state = "PASS" if valid else "FAIL"

    if fw_ref.is_file:
        log.debug("tagging file")
        input_filename = context.get_input_filename("input_file")
        file_ = flywheel_gear_toolkit.utils.metadata.get_file(
            input_filename, context, None
        )
        fail_tag = f"{tag}-FAIL"
        pass_tag = f"{tag}-PASS"
        tag = f"{tag}-{state}"
        input_object = context.get_input("input_file")
        tags = file_.tags
        if state == "PASS" and fail_tag in tags:
            tags.remove(fail_tag)
            context.metadata.update_file(input_filename, tags=tags)
        elif state == "FAIL" and pass_tag in tags:
            tags.remove(pass_tag)
            context.metadata.update_file(input_filename, tags=tags)

        context.metadata.add_file_tags(input_object, str(tag))
    else:
        log.debug("updating container")
        # we do not have an add_qc_result for container other than file so we
        # need to build it the info manually
        # TODO: replace when context.add_qc_result supports all container
        context.metadata.pull_job_info()
        job_info = context.metadata.job_info
        job_info[context.manifest["name"]]["state"] = state
        container = fw_ref.container
        qc = container.info.get("qc", {})
        qc.update(job_info)
        context.metadata.update_container(fw_ref.type, info=qc)
