""" This file holds the class that represents the JSON that we'll be writing to """
# This file holds the class that represents the JSON that we'll be writing to a
# "bigger, better" JSON file.


import json
import os
from typing import Any

from morph.json.incoming import JsonIncoming
from morph.util import cleanup_role_id


class OneTrueJson:
    """A class to hold the data that we'll be writing to a JSON file."""

    def __init__(self, incoming: JsonIncoming):
        self.incoming = incoming
        self.data: dict[str, Any] = {}

        # add data for character_by_id
        self._prepare_role_by_id()

        # add role list to data
        self.data["role_list"] = self.incoming.get_roles_list()

        # add (raw) list of jinxes to data
        self.data["jinxes"] = self.incoming.get_jinx_info()

        # add editions to data
        self.data["editions"] = self.incoming.get_editions()

        # add the team data to the data
        self.data["teams"] = self._prepare_team_data()

    def write(self, output_file: str) -> None:
        """Write the data to a JSON file"""
        print(f"Writing combined JSON data to '{output_file}' …")

        # get the dirname of the filename
        dirname = os.path.dirname(output_file)
        # make sure the directory exists
        os.makedirs(dirname, exist_ok=True)

        # write the data to the file
        with open(output_file, "w", encoding="utf-8") as fhandle:
            json.dump(self.data, fhandle, indent=4, sort_keys=True)
            # make sure we have a newline at the end of the file
            fhandle.write("\n")

    def _prepare_team_data(self) -> dict[str, Any]:
        team_data: dict[str, Any] = {}

        # loop through the role_list
        for role in self.data["role_list"]:
            # if the role doesn't have a team, set it to _Unknown
            if "team" not in role:
                role["team"] = "_Unknown"

            # we'll be storing a list of { id: ..., name: ... } objects in the
            # team_data, so we need to make sure we have an id and a name
            if "id" not in role or "name" not in role:
                # this should never happen, throw an error
                raise ValueError(
                    f"role {role['id']} is missing an id or a name: {role}"
                )

            # if we don't have the role's team in the team_data, add it as an
            # empty list
            if role["team"] not in team_data:
                team_data[role["team"]] = []

            # add the id/name object to the team_data
            team_data[role["team"]].append(
                {
                    "id": role["id"],
                    "name": role["name"],
                }
            )

        return team_data

    def _prepare_role_by_id(self) -> None:
        """Prepare the character_by_id data"""
        # make sure we have a character_by_id key in the data
        if "character_by_id" not in self.data:
            self.data["character_by_id"] = {}

        # this is the base URl for the icons
        image_base_url = (
            "https://raw.githubusercontent.com/rsarvar1a/"
            "json-on-the-clocktower/main/data/images"
        )

        # loop through the roles
        for role in self.incoming.get_roles_list():
            # cleanup the role ID
            role["id"] = cleanup_role_id(role["id"])

            # set the edition for this role
            edition = self.incoming.get_edition_for_role(role["id"])

            # we should have data/icons/{role_id}.png
            if not os.path.exists(f"data/images/{role['id']}.png"):
                raise ValueError(f"Missing image for {role['id']}")
            # set remote_icon to the URL for the icon
            role["remote_image"] = f"{image_base_url}/{role['id']}.png"

            # if we have an edition, but it's None, move on
            if edition is None:
                continue

            # if edition differs from role["edition"], note there's a difference
            if "edition" not in role or edition != role["edition"]:
                # if role["edition"] is missing, set it to {missing}
                # we we don't error on the print() below
                if "edition" not in role:
                    role["edition"] = "{missing}"

                print(
                    f"""edition differs for {role['id']}: "{role['edition']}" vs "{edition}" """
                )

                # set the edition
                role["edition"] = edition

            # if firstNightRemnder is missing, set it to None
            if "firstNightReminder" not in role:
                role["firstNightReminder"] = None
            # if otherNightReminder is missing, set it to None
            if "otherNightReminder" not in role:
                role["otherNightReminder"] = None

            # if firstNightReminder is "" set it to None
            if role["firstNightReminder"] == "":
                role["firstNightReminder"] = None
            # if otherNightReminder is "" set it to None
            if role["otherNightReminder"] == "":
                role["otherNightReminder"] = None

            # set the firstNight value
            role["firstNight"] = self.incoming.get_first_night_order_by_name(
                role["name"]
            )

            # set the otherNight value
            role["otherNight"] = self.incoming.get_other_night_order_by_name(
                role["name"]
            )

            # add the role to the character_by_id data
            self.data["character_by_id"][role["id"]] = role

    def __str__(self):
        """Return a string representation of the data"""
        return json.dumps(self.data, indent=4, sort_keys=True)
