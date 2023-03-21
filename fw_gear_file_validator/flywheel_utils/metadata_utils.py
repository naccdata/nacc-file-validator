from pathlib import Path

from flywheel_gear_toolkit import GearToolkitContext
from flywheel_gear_toolkit.utils.datatypes import Container

from fw_gear_file_validator.flywheel_utils.flywheel_env import PARENT_INCLUDE, HIERARCHY_ORDER


def get_lowest_container_level(levels):
    lowest = max([HIERARCHY_ORDER.index(l) for l in levels])
    return HIERARCHY_ORDER[lowest]


def create_metadata(context: GearToolkitContext, valid: bool, input_object: Container):
    """Populate .metadata.json.

    Args:
        context (GearToolkitContext): The gear context.
        valid: Did the file pass validation?
        input_object: The flywheel container or gear context input file to modify metadata for
    """
    state = "PASS" if valid else "FAIL"

    # Add qc information
    # context.metadata.add_qc_result(file_input, "validation", state=state)

    if input_object["container_type"] == "file":
        updator = context.metadata.update_file
    else:
        updator = context.metadata.update_container
    updator(
        input_object, info={"qc": {"file-validator": {"validation": {"state": state}}}}
    )



def make_fw_metadata(context: GearToolkitContext, container: Container) -> Path:
    """Creates a file that is the json representation of the flywheel hierarchy containing the file and its parents"""
    container_type = container.get("container_type", "file")
    flywheel_meta_object = {container_type: container.to_dict()}
    parents = container.parents
    for parent, p_id in parents.items():
        if p_id is None or parent == "group":
            continue
        getter = getattr(context.client, f"get_{parent}")
        parent_object = getter(p_id)
        flywheel_meta_object[parent] = {
            k: v for k, v in parent_object.to_dict().items() if k in PARENT_INCLUDE
        }
        flywheel_meta_object[parent] = parent_object.to_dict()

    return flywheel_meta_object


def handle_metadata(context, validation_level, valid, tag):
    if validation_level == "flywheel":
        input_object = context.client.get(context.destination["id"])
    else:
        input_object = context.get_input_file_object("input_file")
        context.metadata.add_file_tags(input_object, str(tag))

    create_metadata(context, valid, input_object)
