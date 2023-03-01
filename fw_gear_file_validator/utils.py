import csv
from pathlib import Path
import typing as t

from flywheel_gear_toolkit import GearToolkitContext


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
    context.metadata.add_qc_result(file_input, "file-validator", state=state)
    context.metadata.update_file(file_input)

