import csv
import logging
import typing as t
from pathlib import Path

from fw_gear_file_validator.utils import PARENT_ORDER, FwReference

log = logging.getLogger(__name__)


def add_flywheel_location_to_errors(fw_ref: FwReference, packaged_errors):
    """Takes a set of packaged errors and adds flywheel hierarchy info to them."""
    hierarchy = fw_ref.all
    fw_url = fw_ref.lookup_path
    if fw_ref.is_local():
        for e in packaged_errors:
            e["Flywheel_Path"] = fw_url
            e["Container_ID"] = hierarchy["file"]["file_id"]
    else:
        for e in packaged_errors:
            location = e["Error_Location"].split(".")[0]
            if location not in PARENT_ORDER:
                raise ValueError(
                    f"Value {location} not valid flywheel hierarchy location"
                )
            e["Flywheel_Path"] = fw_url
            id_loc = "file_id" if location == "file" else "id"
            e["Container_ID"] = hierarchy[location][id_loc]


def save_errors(
    errors: t.List[t.Dict], output_dir: t.Union[Path, str], filename: str = None
):
    """Saves the packaged errors to a csv file."""
    if not errors:
        return

    if not isinstance(output_dir, Path):
        output_dir = Path(output_dir)
    error_file = output_dir / filename

    headers = errors[0].keys()

    with open(error_file, "w") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(errors)
