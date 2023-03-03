import csv
import json
import typing as t
from pathlib import Path

from flywheel_gear_toolkit import GearToolkitContext
from fw_gear_file_validator.validators import loaders

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

PARENT_ORDER = ["group", "project", "subject", "session", "acquisition", "analysis", "file"]

def add_flywheel_location_to_errors(flywheel_hierarchy_path, validation_level, errors):

    # Load the hierarchy json
    hierarchy_object = loaders.JsonLoader(flywheel_hierarchy_path).load()
    # If validation level is flywheel, then the input_file_object should have every parent object
    parents = {}
    for parent_level in hierarchy_object.keys():
        if parent_level == "file":
            parents[parent_level] = hierarchy_object[parent_level].get('name', None)
            continue
        parents[parent_level] = hierarchy_object[parent_level].get('label', None)

    ordered_parents = [parents[order] for order in PARENT_ORDER if order in parents]
    # if the validation level was the file, we just need to add the same flywheel path to every error
    if validation_level == "file":
        fw_url = "fw://" + "/".join(ordered_parents)
        for e in errors:
            e["Flywheel_Path"] = fw_url
            e["Container_ID"] = hierarchy_object['file']['file_id']

    # If the validation level was on Flywheel, that means it was a json schema and we can use the first level of
    # Error_Location to get the level.  This is a bit complicated but so is adding flywheel specific error stuff
    # to general schema error handling.

    elif validation_level == "flywheel":
        for e in errors:
            location = e['Error_Location'].split('.')[0]
            if location not in PARENT_ORDER:
                raise ValueError(f"Value {location} not valid flywheel hierarchy location")

            ordered_parents = [parents[order] for order in PARENT_ORDER[:PARENT_ORDER.index(location)+1] if order in parents]
            fw_url = "fw://" + "/".join(ordered_parents)
            e["Flywheel_Path"] = fw_url
            if location == "file":
                id_location = "file_id"
            else:
                id_location = "id"

            e["Container_ID"] = hierarchy_object[location][id_location]

    return errors





def save_errors(errors: t.List[t.Dict], output_dir: t.Union[Path, str]):
    if not errors:
        return

    if not isinstance(output_dir, Path):
        output_dir = Path(output_dir)
    error_file = output_dir / "file_validator_errors.csv"

    headers = errors[0].keys()

    with open(error_file, "w") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(errors)


def create_metadata(context: GearToolkitContext, valid: bool, file_input: t.Dict):
    """Populate .metadata.json.

    Args:
        context (GearToolkitContext): The gear context.
        valid: Did the file pass validation?
        file_input: The gear context input file to modify metadata for
    """
    state = "PASS" if valid else "FAIL"

    # Add qc information
    # context.metadata.add_qc_result(file_input, "validation", state=state)
    context.metadata.update_file(
        file_input, info={"qc": {"file-validator": {"validation": state}}}
    )


def make_fw_metadata_file(
        context: GearToolkitContext, gear_file_object: t.Dict
) -> Path:

    file_id = gear_file_object["object"]["file_id"]
    flywheel_file = context.client.get_file(file_id)
    flywheel_meta_object = {'file': flywheel_file.to_dict()}
    parents = flywheel_file.parents
    for parent, p_id in parents.items():
        if p_id is None:
            continue
        getter = getattr(context.client, f"get_{parent}")
        parent_object = getter(p_id)
        flywheel_meta_object[parent] = {k: v for k, v in parent_object.to_dict().items() if k in PARENT_INCLUDE}
        flywheel_meta_object[parent] = parent_object.to_dict()

    file_out = context.work_dir / "fw_object.json"
    with open(file_out, "w") as json_out:
        json.dump(flywheel_meta_object, json_out, indent=4, sort_keys=True, default=str)

    return file_out