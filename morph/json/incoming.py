""" Load data from multiple JSON sources (local and remote) and combine them """
# a JsonIncoming class is used to load data from multiple JSON sources (local and remote)
# and combine them into a single data structure for use by the rest of the program -
# JsonOutgoing


import json
import os
from typing import Any, Optional

from morph.util import configure_logger, fetch_remote_data, load_data

LOGGER = configure_logger(__name__)
LOGGER.debug("Logging started for %s", LOGGER.name)


class JsonIncoming:
    """Load data from multiple JSON sources (local and remote) and combine them
    into a single data structure for use by the rest of the program -
    JsonOutgoing"""

    def __init__(self, force_fetch: bool = False):
        """A class to hold the data that we'll be writing to a JSON file."""
        self.data: dict[Any, Any] = {}
        self.force_fetch = force_fetch

        # load the data
        self._load()

        # cleanup to avoid having some data we don't need (because we derive it
        # from other data)
        self._cleanup()

        # work out the night order lookup
        self._make_night_order_lookup()

    def get_script_nightorder_data(self) -> dict:
        """Get the script night order data"""
        return self.data["external"]["script-nightorder"]

    def get_first_night_order_by_name(self, name: str) -> Optional[int]:
        """Get the first night order by name"""
        # if we don't have a first night order, return None
        if name not in self.data["night_order_lookup"]["first"]:
            return None
        return self.data["night_order_lookup"]["first"][name]

    def get_other_night_order_by_name(self, name: str) -> Optional[int]:
        """Get the other night order by name"""
        # if we don't have an other night order, return None
        if name not in self.data["night_order_lookup"]["other"]:
            return None
        return self.data["night_order_lookup"]["other"][name]

    def get_roles_list(self) -> list:
        """Get the roles list"""
        return self.data["roles_list"]

    def get_edition_for_role(self, role_id: str) -> Optional[str]:
        """Get the edition for a role"""
        # if we don't have an edition for this role, return None
        if role_id not in self.data["edition-lookup"]:
            return None

        edition = self.data["edition-lookup"][role_id]

        if edition == "":
            edition = "experimental"

        return edition

    def get_jinx_info(self) -> list:
        """Get the jinx info"""
        return self.data["external"]["script-jinx"]

    def get_editions(self) -> list:
        """Get the editions"""
        return self.data["editions"]

    def _load(self) -> None:
        """Load data from multiple JSON sources (local and remote) and combine
        them into a single data structure for use by the rest of the program -
        JsonOutgoing"""
        # fetch the remote data
        self._fetch_remote_data()

        # load the local data
        self._load_local_data()

    def _make_night_order_lookup(self) -> None:
        """We want a night order lookup (by name, not through choice)"""
        # we need self.night_order_lookup to be a dict with
        # keys: first, and other
        # values: a dict of role name -> order number
        self.data["night_order_lookup"] = {
            "first": {},
            "other": {},
        }

        # get the night order data
        night_order_data = self.get_script_nightorder_data()

        # loop through firstNight, with the index as the position
        for index, role_id in enumerate(night_order_data["firstNight"]):
            night_position = index + 1
            # store the position in the dict
            self.data["night_order_lookup"]["first"][role_id] = night_position

        # loop through otherNight, with the index as the position
        for index, role_id in enumerate(night_order_data["otherNight"]):
            night_position = index + 1
            # store the position in the dict
            self.data["night_order_lookup"]["other"][role_id] = night_position

    def _cleanup(self) -> None:
        """Cleanup to avoid having some data we don't need (because we derive it
        from other data)"""

        # set firstNight and otherNight to None
        for role in self.data["roles_list"]:
            # set firstNight to None
            if "firstNight" in role:
                role["firstNight"] = None
            # set otherNight to None
            if "otherNight" in role:
                role["otherNight"] = None

        # if "image" is "[Your direct URL here]" then set it to None
        for role in self.data["roles_list"]:
            if "image" in role and role["image"] == "[Your direct URL here]":
                role["image"] = None

    def _fetch_remote_data(self):
        """Fetch remote data and save in data/external/"""
        remote_data = {
            "bra1n-roles": "https://raw.githubusercontent.com/bra1n/townsquare/develop/src/roles.json",  # pylint: disable=line-too-long
            "bra1n-fabled": "https://raw.githubusercontent.com/bra1n/townsquare/develop/src/fabled.json",  # pylint: disable=line-too-long
            "script-nightorder": "https://script.bloodontheclocktower.com/data/nightsheet.json",  # pylint: disable=line-too-long
            "script-jinx": "https://script.bloodontheclocktower.com/data/jinx.json",  # pylint: disable=line-too-long
        }

        for name, url in remote_data.items():
            local_dir = "data/external"
            local_path = f"{local_dir}/{name}.json"

            # make sure the directory exists
            os.makedirs("data/external", exist_ok=True)

            # if we're using force_fetch, or we don't have the file, fetch it
            # if we do, just say so
            if os.path.exists(local_path) and not self.force_fetch:
                LOGGER.info(
                    "Skipping remote fetch for '%s';"
                    " it already exists locally as '%s'",
                    name,
                    local_path,
                )

            else:
                LOGGER.info("Fetching %s from %s …", name, url)
                data = fetch_remote_data(url)
                # write the data to a file
                with open(local_path, "w", encoding="utf-8") as fhandle:
                    LOGGER.debug("Writing %s to %s …", name, local_path)
                    json.dump(data, fhandle, indent=4, sort_keys=True)

            # either way we now have the file so we can load it and add it to self.data.external
            LOGGER.info("Loading %s from %s …", name, local_path)
            data = load_data(local_path)

            # make self.data.external if it doesn't exist
            if "external" not in self.data:
                self.data["external"] = {}

            # add the data to self.data.external
            self.data["external"][name] = data

    def _load_edition_data(self) -> None:
        # we need to load data/role-edition.json
        # and add it to self.data.edition
        filename = "data/role-edition.json"
        LOGGER.info("Loading %s …", filename)
        data_roleedition = load_data(filename)
        self.data["edition-lookup"] = data_roleedition

        # load the edition meta data from data/edition-info.json
        filename = "data/edition-info.json"
        LOGGER.info("Loading %s …", filename)
        data_info = load_data(filename)
        self.data["edition-info"] = data_info
        # print a json dump of edition-info
        # print(json.dumps(data_info, indent=4, sort_keys=True))

        # loop through the data and add to self.data.editions
        # where the key is the edition and the value is a dict of id and name
        self.data["editions"] = {}
        for role_id, edition in data_roleedition.items():
            if edition == "":
                edition = "experimental"
            # if the edition isn't in self.data.editions, add it
            if edition not in self.data["editions"]:
                LOGGER.debug("Adding %s to self.data.editions …", edition)
                # we will have a meta block for the edition
                self.data["editions"][edition] = {}
                LOGGER.debug(self.data["edition-info"][edition])
                self.data["editions"][edition]["_meta"] = self.data["edition-info"][
                    edition
                ]
            # if the role_id isn't in self.data.editions[edition], add it
            if role_id not in self.data["editions"][edition]:
                self.data["editions"][edition][role_id] = {
                    "id": role_id,
                    "name": role_id,
                    "physicaltoken": self.data["edition-info"][edition][
                        "physicaltokens"
                    ],
                }

    def _get_role_files(self) -> list[str]:
        """get a list of json files that contain role information"""
        # these are the main files with ROLE information in them
        role_files = [
            "data/external/bra1n-roles.json",
            "data/external/bra1n-fabled.json",
            "data/roles-nightmeta.json",
        ]
        # add anything in the extra-characters directory
        for filename in os.listdir("data/extra-characters"):
            if filename.endswith(".json"):
                role_files.append(f"data/extra-characters/{filename}")

        return role_files

    def _edition_sanity_check(self, data, source_file) -> None:
        # loop through the list of roles
        for role in data:
            # - warn about anything that doesn't have an edition
            if "edition" not in role:
                LOGGER.debug(
                    "role '%s' has no edition field in the source data [%s]",
                    role["id"],
                    source_file,
                )
                continue

            # - warn if the edition is an empty string
            if role["edition"] == "":
                LOGGER.debug(
                    "role '%s' has an empty string for the edition field in the source data [%s]",
                    role["id"],
                    source_file,
                )

    def _load_local_data(self):
        """Load data from local JSON files"""

        # load the edition data
        self._load_edition_data()

        # load roles from various files
        local_roledata_files = self._get_role_files()

        # load the local data
        for filename in local_roledata_files:
            LOGGER.info("Loading %s …", filename)
            data = load_data(filename)

            # sanity check the edition data
            self._edition_sanity_check(data, filename)

            # we'll store the roles in self.data.roles
            if "roles_list" not in self.data:
                self.data["roles_list"] = []

            # extend the roles_list with the roles from the file
            self.data["roles_list"].extend(data)

        # we've loaded data from all the file sources we know about
        LOGGER.info("Loaded %d roles", len(self.data["roles_list"]))

    def __str__(self):
        """Return a string representation of the data"""
        return json.dumps(self.data, indent=4, sort_keys=True)
