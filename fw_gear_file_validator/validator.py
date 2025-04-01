"""validator.py.

Creates validators for different object/file types
"""

import json
import typing as t
from pathlib import Path

import jsonschema
from jsonschema.exceptions import ValidationError

from fw_gear_file_validator import errors as err
from fw_gear_file_validator import utils

# We are not supporting array, object, or null.
JSON_TYPES = {"string": str, "number": float, "integer": int, "boolean": bool}


class JsonValidator:
    """Json Validator class."""

    def __init__(self, schema: t.Union[dict, Path, str]):
        """Initializes a JsonValidator Object."""
        if isinstance(schema, str):
            schema = Path(schema)
        if isinstance(schema, Path):
            with open(schema, "r", encoding="UTF-8") as schema_instance:
                schema = json.load(schema_instance)
        self.validator = jsonschema.Draft7Validator(schema)

    def validate_file_not_empty(
        self, file_contents: t.Union[dict, list, None]
    ) -> t.Tuple[bool, t.List[dict]]:
        """Validates if a file is empty.  Empty means no bytes were read in the content.

        Args:
            file_contents: the data read from the file in dict or list format.

        Returns:
            bool: True if valid, false if not
            list[dict] or None:  An "empty file" error if the file is empty, else None.

        """
        # An empty json will load as {}, an empty csv will load as [].  Both can be caught with a not statement.
        if not file_contents:
            return False, self.handle_errors([err.make_empty_file_error()])
        return True, []

    def validate(self, d: dict) -> t.Tuple[bool, t.List[t.Dict]]:
        """Performs validation on a dict.

        Args:
            d: the dictionary to process

        Returns:
            valid: True if valid, False otherwise
            errors: any errors reported during validation

        """
        valid, empty_error = self.validate_file_not_empty(d)
        if not valid:
            return valid, empty_error

        valid, errors = self.process_item(d)

        return valid, errors

    def process_item(self, d: dict) -> t.Tuple[bool, t.List[t.Dict]]:
        """Processes contents of dict and returns a tuple of valid and formatted errors.

        Args:
            d (dict): python dictionary created from a json object

        Returns:
            (bool): True if valid, false if errors are present
            (list[dict] or None): a list of errors or and empty list

        """
        errors = list(self.validator.iter_errors(d))
        if errors:
            errors = self.handle_errors(errors)
        valid = False if errors else True
        return valid, errors

    @staticmethod
    def handle_errors(file_errors: list[ValidationError]) -> t.List[t.Dict]:
        """Processes errors into a standard output format.

        A jsonschema error in python has the following data structure:
        {
            'message': '[1, 2, 3, 4] is too long',
             'path': deque(['list']),
             'relative_path': deque(['list']),
             'schema_path': deque(['properties', 'list', 'maxItems']),
             'relative_schema_path': deque(['properties', 'list', 'maxItems']),
             'context': [],
             'cause': None,
             'validator': 'maxItems',
             'validator_value': 3,
             'instance': [1, 2, 3, 4],
             'schema': {'type': 'array', 'maxItems': 3},
             'parent': None,
             '_type_checker': <TypeChecker types={'array', 'boolean', 'integer', 'null', 'number', 'object', 'string'}>
         }.

        This must be converted to the FW Error standard:
        type: str – “error” (always error)
        code: str – Type of the error (e.g. MaxLength)
        location: str – Location of the error
        flywheel_path: str – Flywheel path to the container/file
        container_id: str – ID of the source container/file
        value: str – current value
        expected: str – expected value
        message: str – error message description
        Additionally, the value for location will be formatted as such:
        For JSON input file: { “key_path”: string }, with string being the JSON key

        The flywheel relative items will be handled by a later function.
        They are omitted here to keep json validator flywheel client independent.
        These items are:
            - flywheel_path
            - container_id

        """
        file_errors = sorted(file_errors, key=lambda e: e.path)

        error_report = []
        for error in file_errors:
            error_report.append(err.validator_error_to_standard(error))
        return error_report


class CsvValidator(JsonValidator):
    """CSV Validator class."""

    def __init__(self, schema: t.Union[dict, Path, str]):
        """Initializes a CsvValidator object."""
        super().__init__(schema)

    def get_column_dtypes(self) -> dict[str:type]:
        """Get the specified datatypes of each csv column from a Json Schema.

        Returns:
            A dictionary containing {column-name : python type} for every column

        """
        column_types = {}
        schema = self.validator.schema
        for schema_property, property_val in schema["properties"].items():
            if "$ref" in property_val:
                _, property_val = self.validator.resolver.resolve(property_val["$ref"])
            json_type = property_val.get("type")
            column_types[schema_property] = self.convert_json_types_to_python(json_type)
        return column_types

    @staticmethod
    def convert_json_types_to_python(json_type: str) -> type:
        """Converts json types to python types as best as possible.

            Conversion table:
            | JSON    | Python |
            |---------|--------|
            | string  | str    |
            | number  | float  |
            | integer | int    |
            | boolean | bool   |
            | null    | None   |

        Args:
            json_type: a json type specified by the schema

        Returns:
            a python type-equivalent of the specified json-type

        """
        if isinstance(json_type, list):
            raise ValueError(
                "Multiple possible datatypes not allowed for csv validation.  Check your schema."
            )
        return JSON_TYPES.get(json_type, str)  # default to type str if not supported

    def validate(
        self, csv_dicts: t.List[t.Dict], drop_empty: bool = True
    ) -> t.Tuple[bool, t.List[t.Dict]]:
        """Performs the validation of a CSV file.

        Args:
            csv_dicts: the list of dicts generated by csv.DictReader

        Returns:
            valid: True if no errors, False otherwise.
            errors: Any errors generated during validation.


        """
        valid, empty_error = self.validate_file_not_empty(csv_dicts)
        if not valid:
            return valid, empty_error

        valid, header_errors = self.validate_header(csv_dicts)
        if not valid:
            return valid, header_errors

        if drop_empty:
            csv_dicts = [{k: v for k, v in row.items() if v} for row in csv_dicts]

        valid, errors = self.process_file(csv_dicts)

        return valid, errors

    def validate_header(self, csv_dicts: t.List[t.Dict]) -> t.Tuple[bool, list]:
        """Checks that the header is valid.

        Valid is a combination of two checks:
        1. is the header present?
        2. does it have any columns NOT specified in the schema.

        NOTE:  This does NOT address the situation where the csv has only a subset
        of the specified columns in the schema.  You can enforce column requirements by making them
        required in the schema...I think.

        Args:
            csv_dicts (list[dict]): the csv data as read by csv.DictReader, where each row is a dictionary in a list of dictionaries,
            and the dictionary's keys are the csvs headers.

        Returns:
            (bool): True if the header passes validation, False otherwise
            (list[dict] or None): A Header error if present or None if the file passes validation

        """
        actual_columns = csv_dicts[0].keys()
        expected_columns = self.validator.schema["properties"].keys()
        column_is_in_schema = [ac in expected_columns for ac in actual_columns]

        # If all the present columns are in the schema, no need to continue checking.
        if all(column_is_in_schema):
            return True, []

        # if none of the columns are in the schema, we assume this is missing its header:
        if not any(column_is_in_schema):
            return False, self.handle_errors([err.make_missing_header_error()])

        # If we've made it here, some but not all values are false:
        column_errors = [
            err.make_incorrect_header_error(cname)
            for cname, present in zip(actual_columns, column_is_in_schema)
            if not present
        ]

        return False, self.handle_errors(column_errors)

    def process_file(self, csv_dicts: t.List[t.Dict]):
        """Processes the csv file one row at a time.

        Since each row can be considered its own little json file, we need to call the Parent JsonValidator's
        "process_item" once for each row and concatenate all errors.

        Args:
            csv_dicts: the list of csv row dictionaries to process

        Returns:
            (bool): True if valid (no errors), false otherwise
            (list(dict) or None): a list of errors detected, or None

        """
        csv_valid = True
        csv_errors = []
        column_types = self.get_column_dtypes()
        for (
            row_num,
            row_contents,
        ) in enumerate(csv_dicts):
            cast_row = {
                key: utils.cast_csv_val(value, column_types.get(key, str))
                for key, value in row_contents.items()
            }
            valid, errors = self.process_item(cast_row)
            csv_valid = csv_valid & valid
            self.add_csv_location_spec(row_num, errors)
            csv_errors.extend(errors)
        return csv_valid, csv_errors

    @staticmethod
    def add_csv_location_spec(
        row_num: int, row_errors: t.Union[t.List[t.Dict], None]
    ) -> None:
        """Include the row number in the 'location' element of the error.

        Args:
            row_num (int): the row number that the error came from
            row_errors (list(dict)):  any errors associated with this row

        """
        for error in row_errors:
            # The old location will be something like "{'key_path': 'properties.Col2'}"
            # We just want the column name (Col2), so we extract it like this:
            if not error["location"]:
                error["location"] = ""
            else:
                col_name = error["location"]["key_path"].split(".")[-1]
                error["location"] = {"line": row_num + 1, "column_name": col_name}


def initialize_validator(
    file_type: str, schema: t.Union[dict, Path, str]
) -> t.Union[JsonValidator, CsvValidator]:
    """Initialize the validator.

    In the future we may implement a recursive subclass factory (or something),
    but for two validators the code does not require that complexity.

    Args:
        file_type: the type of file we're validating
        schema: the validation JSON schema file.

    Returns:
        JsonValidator | CsvValidator

    """
    if file_type == "json":
        return JsonValidator(schema)
    elif file_type == "csv":
        return CsvValidator(schema)
    else:
        raise ValueError("file type " + file_type + " Not supported")
