import csv
import logging
import typing as t
from pathlib import Path
from flywheel import models
from flywheel_gear_toolkit import GearToolkitContext

from fw_gear_file_validator.utils import PARENT_ORDER, FwReference

log = logging.getLogger(__name__)

AnyContainer = [models.project, models.subject, models.session, models.acquisition, models.analysis, models.file]


def validate_file_contents(fw_ref) -> bool:
        """Returns True if the object is a local file, False otherwise."""
        if fw_ref.file_path:
            return True
        return False

def add_flywheel_location_to_errors(fw_ref: FwReference, packaged_errors):
    """Takes a set of packaged errors and adds flywheel hierarchy info to them."""
    hierarchy = fw_ref.hierarchy_objects
    fw_url = fw_ref.get_lookup_path()
    if validate_file_contents():
        for e in packaged_errors:
            e["flywheel_path"] = fw_url
            e["container_id"] = hierarchy["file"]["file_id"]
    else:
        for e in packaged_errors:
            # This may be broken with our new implementation
            location = e["location"].split(".")[0]
            if location not in PARENT_ORDER:
                raise ValueError(
                    f"Value {location} not valid flywheel hierarchy location"
                )
            e["flywheel_path"] = fw_ref.get_lookup_path(level=location)
            id_loc = "file_id" if location == "file" else "id"
            e["container_id"] = hierarchy[location][id_loc]

    return packaged_errors


def save_errors_csv(
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

    log.debug(f"saved errors to {error_file}")


def save_errors_metadata(errors: t.List[t.Dict], input_file: FwReference, gtk_context: GearToolkitContext):
    """Saves the packaged errors to file metadata.

    """
    if not errors:
        state = "PASS"
        meta_dict = {}
    else:
        state = "FAIL"
        meta_dict = {"data": errors}

    gtk_context.metadata.add_qc_result(input_file.name, "validation", state=state, data=meta_dict)

