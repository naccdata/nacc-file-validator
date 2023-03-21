from dataclasses import dataclass

PARENT_INCLUDE = [
    # General values
    "label",
    "info",
    "uid",
    # Session values
    "age",
    "weight",
    # Subject values
    "sex",
    "cohort",
    "mlset",
    "ethnicity",
    "species",
    "strain",
    "code",
    "firstname",
    "lastname",
]
PARENT_ORDER = [
    "group",
    "project",
    "subject",
    "session",
    "acquisition",
    "analysis",
    "file",
]


@dataclass
class FwReference:
    dest_id: str = None
    dest_type: str = None
    file_id: str = None
    file_name: str = None
    file_type: str = None

    @property
    def is_file(self):
        return self.file_id is not None


@dataclass
class FwLoaderConfig:
    add_parents: bool = False
    validation_level: str = "file"
