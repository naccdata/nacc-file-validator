import csv
import typing as t
from pathlib import Path

from fw_gear_file_validator.flywheel_utils.flywheel_env import PARENT_ORDER


def add_flywheel_location_to_errors(hierarchy_object, validation_level, errors):
    """Takes a set of packaged errors and adds flywheel hierarchy information to them.

    If validation was run at the "flywheel" level, then validation was done on a json schema.
    When this creates flywheel URLs for that, it relies heavily on the predictable structure
    of that schema.
    """

    # If validation level is flywheel, then the input_file_object should have every parent object
    parents = {}
    for parent_level in hierarchy_object.keys():
        if parent_level == "file":
            parents[parent_level] = hierarchy_object[parent_level].get("name", None)
            continue
        parents[parent_level] = hierarchy_object[parent_level].get("label", None)

    ordered_parents = [parents[order] for order in PARENT_ORDER if order in parents]
    # if the validation level was the file, we just need to add the same flywheel path to every error
    if validation_level == "file":
        fw_url = "fw://" + "/".join(ordered_parents)
        for e in errors:
            e["Flywheel_Path"] = fw_url
            e["Container_ID"] = hierarchy_object["file"]["file_id"]

    # If the validation level was on Flywheel, that means it was a json schema and we can use the first level of
    # Error_Location to get the level.  This is a bit complicated but so is adding flywheel specific error stuff
    # to general schema error handling.

    elif validation_level == "flywheel":
        for e in errors:
            location = e["Error_Location"].split(".")[0]
            if location not in PARENT_ORDER:
                raise ValueError(
                    f"Value {location} not valid flywheel hierarchy location"
                )

            ordered_parents = [
                parents[order]
                for order in PARENT_ORDER[: PARENT_ORDER.index(location) + 1]
                if order in parents
            ]
            fw_url = "fw://" + "/".join(ordered_parents)
            e["Flywheel_Path"] = fw_url
            if location == "file":
                id_location = "file_id"
            else:
                id_location = "id"

            e["Container_ID"] = hierarchy_object[location][id_location]

    return errors


def save_errors(errors: t.List[t.Dict], output_dir: t.Union[Path, str]):
    """Saves the packaged errors to a csv file"""
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
