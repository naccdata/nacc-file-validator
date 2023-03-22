import copy
import typing as t

from flywheel_gear_toolkit import GearToolkitContext

from fw_gear_file_validator.flywheel_utils.flywheel_env import (
    FwLoaderConfig,
    FwReference,
)
from fw_gear_file_validator.flywheel_utils.metadata_utils import (
    get_lowest_container_level,
    make_fw_metadata,
)
from fw_gear_file_validator.validator_utils.file_loaders import FileLoader


class FwLoader:
    def __init__(
        self,
        context: GearToolkitContext,
        config: FwLoaderConfig,
    ):
        self.context = context
        self.add_parents = config.add_parents
        self.validation_level = config.validation_level

    def _get_fw_meta_dict(self, fw_reference):
        """Get the flywheel metadata dictionary.  Needed for logging and possibly for validation"""
        if fw_reference.is_file:
            starting_container = self.context.client.get_file(fw_reference.file_id)
        else:
            ctype = fw_reference.dest_type
            cid = fw_reference.dest_id
            starting_container = self.context.__getattribute__(f"get_{ctype}")(cid)

        return make_fw_metadata(self.context, starting_container)

    def load(self, fw_reference: FwReference) -> t.Tuple[dict, dict]:
        # Loader is now has flywheel dependencies, mixing the two together increases complexity of
        # loading logic.

        full_fw_meta = self._get_fw_meta_dict(fw_reference)

        # Case 0: we're validating a flywheel object with parents,
        # so we're just returning the fw_meta dict
        validation_dict = copy.deepcopy(full_fw_meta)

        # Case 1, we're validating a file contents, with flywheel parents, so we replace the
        # "file" flywheel object with the actual contents of the file itself
        if self.validation_level == "file":
            # Here we replace the "file" object with the loaded filedata
            file_dict = self.load_local_file_contents(
                fw_reference.input_name, fw_reference.file_type
            )
            validation_dict["file"] = file_dict

        # Case 2/3, we're validating any of the above without the parents in the hierarchy
        if not self.add_parents:
            validation_dict = self.remove_parents_from_dict(validation_dict)

        return full_fw_meta, validation_dict

    def load_local_file_contents(self, input_name: str, file_type: str):
        file_path = self.context.get_input_path(input_name)
        loader = FileLoader.factory(file_type)
        file_dict = loader.load(file_path)
        return file_dict

    @staticmethod
    def remove_parents_from_dict(hierarchy_dict):
        levels = list(hierarchy_dict.keys())
        lowest = get_lowest_container_level(levels)
        for level in levels:
            if level == lowest:
                continue
            del hierarchy_dict[level]

        # Finally, since we've removed all parents, we no longer need the dictionary to contain
        # the level that it's at, that's redundant.
        # so {"file": {<file_object>}} just becomes {<file_object>}
        hierarchy_dict = hierarchy_dict[lowest]

        return hierarchy_dict
