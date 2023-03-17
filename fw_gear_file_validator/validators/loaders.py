import json
import typing as t
from abc import ABC, abstractmethod
from pathlib import Path

from flywheel_gear_toolkit import GearToolkitContext

from fw_gear_file_validator.utils import make_fw_metadata


class FwLoader:
    def __init__(
        self,
        context: GearToolkitContext,
        strategy: str,
        add_parents: bool = True,
        input_file_key: str = None,
    ):
        self.context = context
        self.strategy = strategy
        self.add_parents = add_parents

        if not input_file_key:
            input_file_key = ""
        self.input_file_key = input_file_key
        self.fw_meta_dict = self._get_fw_meta_dict()

    def _get_fw_meta_dict(self):
        """Get the flywheel metadata dictionary.  Needed for logging and possibly for validation"""
        if self.input_file_key:
            input_file_object = self.context.get_input(self.input_file_key)
            starting_container = self.context.client.get_file(
                input_file_object["object"]["file_id"]
            )
        else:
            ctype = self.context.destination["type"]
            cid = self.context.destination["id"]
            starting_container = self.context.__getattribute__(f"get_{ctype}")(cid)

        return make_fw_metadata(self.context, starting_container)

    def load(self):
        # Loader is now has flywheel dependencies, mixing the two together increases complexity of
        # loading logic.
        if self.strategy == "local-file":
            return self._load_local_file()
        elif self.add_parents:
            return self.fw_meta_dict
        elif self.strategy == "flywheel-file":
            return self._load_flywheel_file()
        elif self.strategy == "flywheel-container":
            return self._load_flywheel_container()

        raise ValueError("Invalid Loader Settings")

    def _load_flywheel_file(self) -> t.Dict:
        # Otherwise isolate the target object (file if present, or the destination container)
        ctype = (
            "file" if "file" in self.fw_meta_dict else self.context.destination["type"]
        )
        return {ctype: self.fw_meta_dict[ctype]}

    def _load_flywheel_container(self) -> t.Dict:
        # Otherwise isolate the target object (file if present, or the destination container)
        ctype = self.context.destination["type"]
        return {ctype: self.fw_meta_dict[ctype]}

    def _load_local_file(self) -> t.Dict:
        """Loads the file and returns it as a dict."""
        # Loader now doesn't work with anything other than flywheel gears
        file_path = self.context.get_input_path(self.input_file_key)
        with open(file_path, "r", encoding="UTF-8") as file_instance:
            file_object = json.load(file_instance)
        return file_object
