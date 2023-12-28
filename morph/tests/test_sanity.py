""" Tests to ensure some basic generated file sanity """

import json
import os
import pytest
import requests


def in_github_actions():
    """Check if we're running in GitHub Actions"""
    return os.environ.get("GITHUB_ACTIONS", "false") == "true"


class TestJsonData:
    """Tests for the contents of the generated JSON data."""

    @classmethod
    def setup_class(cls):
        """Load the JSON data from the file."""
        cls.json_data: dict  # type: ignore
        cls.data_file: str = "data/generated/roles-combined.json"  # type: ignore

        assert os.path.exists(cls.data_file)

        # open the data file
        with open(cls.data_file, "r", encoding="utf-8") as data_file:
            # load the data
            cls.json_data = json.load(data_file)

        # check the data is loaded
        assert cls.json_data is not None

        # keep track of the URLs we've checked
        cls._checked_urls = set()

    def test_top_level_keys(self):
        """Test that the top-level keys in the data file are as expected."""

        # check that the keys are as expected
        assert set(self.json_data.keys()) == set(
            [
                "character_by_id",
                "editions",
                "jinxes",
                "role_list",
                "teams",
            ]
        )

    def test_missing_info(self):
        """Make sure we have all the info we need for each role in the expected places"""

        # for the id of each  role in the role_list, we should have a
        # corresponding entry in character_by_id
        for role in self.json_data["role_list"]:
            role_id = role.get("id", None)
            assert role_id is not None
            assert (
                role_id in self.json_data["character_by_id"]
            ), f"Missing role_id '{role_id}' in character_by_id, exists in role_list"

    def test_some_characterbyid_keys(self):
        """Test that some of the values in the data file are as expected."""

        # we expect DAWN, DEMON, DUSK, acrobat, highpriestess, knight,
        # vizier, recluse as a subset of the keys in character_by_id; we
        # don't care about extra keys, we're just looking for these ones
        # for now
        # - we test them one by one so it's obvious where the failure is!
        expected_keys = [
            "DAWN",
            "DEMON",
            "DUSK",
            "acrobat",
            "recluse",
        ]

        # we want to always test for extra-characters, so we don't miss
        # them if they're added
        # - get the list of files in data/extra-characters
        # - for each file, load the json
        # - for each json add the id to expected_keys
        extra_characters_dir = "data/extra-characters"
        assert os.path.exists(extra_characters_dir)
        for filename in os.listdir(extra_characters_dir):
            if filename.endswith(".json"):
                with open(
                    os.path.join(extra_characters_dir, filename), "r", encoding="utf-8"
                ) as extra_characters_file:
                    extra_characters_json = json.load(extra_characters_file)
                    expected_keys.append(extra_characters_json[0]["id"])

        # sort and uniq the list
        expected_keys = sorted(list(set(expected_keys)))

        for key in expected_keys:
            assert (
                key in self.json_data["character_by_id"]
            ), f"Missing key '{key}' in character_by_id, expected in expected_keys"

    def test_editions_keys(self):
        """Test that the editions keys are as expected"""
        # we expect _exactly_ these keys in editions
        # "", "_meta" "bmr" "ks" "snv" "tb"
        assert set(["experimental", "_meta", "bmr", "ks", "snv", "tb", "base3"]) == set(
            self.json_data["editions"].keys()
        )

    def test_some_edition_experimental_keys(self):
        """Test that some of the keys in the experimental edition are as expected"""
        # some of the keys in the experimental edition are: acrobat, goblin,
        # highpriestess, organgrinder, widow
        expected_keys = [
            "acrobat",
            "goblin",
            "highpriestess",
            "organgrinder",
            "widow",
        ]
        # ).issubset(set(data["editions"]["experimental"].keys()))
        for key in expected_keys:
            assert key in self.json_data["editions"]["experimental"]

    def test_some_edition_meta_keys(self):
        """Test that some of the keys in the _meta edition are as expected"""
        # some of the keys in the _meta edition are: DAWN, DEMON, DUSK,
        # MINION
        expected_keys = ["DAWN", "DEMON", "DUSK", "MINION"]
        for key in expected_keys:
            assert key in self.json_data["editions"]["_meta"]

    def test_some_edition_bmr_keys(self):
        """Test that some of the keys in the bmr edition are as expected"""
        # some of the keys in the bmr edition are: assassin, bishop, fool,
        # gambler, po, voudon
        expected_keys = ["assassin", "bishop", "fool", "gambler", "po", "voudon"]
        for key in expected_keys:
            assert key in self.json_data["editions"]["bmr"]

    def test_some_edition_ks_keys(self):
        """Test that some of the keys in the ks edition are as expected"""
        # some of the keys in the ks edition are: atheist, boomdandy,
        # damsel, farmer
        expected_keys = ["atheist", "boomdandy", "damsel", "farmer"]
        for key in expected_keys:
            assert key in self.json_data["editions"]["ks"]

    def test_some_edition_snv_keys(self):
        """Test that some of the keys in the snv edition are as expected"""
        # some of the keys in the snv edition are: artist, barber, barista,
        # klutz, mutant, nodashii
        expected_keys = [
            "artist",
            "barber",
            "barista",
            "klutz",
            "mutant",
            "nodashii",
        ]
        for key in expected_keys:
            assert key in self.json_data["editions"]["snv"]

    def test_some_edition_tb_keys(self):
        """Test that some of the keys in the tb edition are as expected"""
        # some of the keys in the tb edition are: baron, beggar, butler,
        # chef, spy, imp, bureaucrat
        expected_keys = [
            "baron",
            "beggar",
            "butler",
            "chef",
            "spy",
            "imp",
            "bureaucrat",
        ]
        for key in expected_keys:
            assert key in self.json_data["editions"]["tb"]

    def test_editions_meta_special_cases(self):
        """Test that the special cases in the _meta edition are as expected"""
        # every edition should have a "_meta" key
        for edition in self.json_data["editions"]:
            assert "_meta" in self.json_data["editions"][edition]

        # each entry in editions that's NOT _meta should have id, name, physicaltoken keys
        for edition in self.json_data["editions"]:
            for role in self.json_data["editions"][edition]:
                if role != "_meta":
                    assert "id" in self.json_data["editions"][edition][role]
                    assert "name" in self.json_data["editions"][edition][role]
                    assert "physicaltoken" in self.json_data["editions"][edition][role]

    def remote_image_checks(self, url):
        """Check that the given URL is a sane remote image URL"""
        # do nothing if we've already checked this URL
        if self.url_already_checked(url):
            return

        response = requests.head(url, timeout=5)
        assert (
            response.status_code == 200
        ), f"URL '{url}' returned non-200 response: {response.status_code}"
        assert (
            response.headers["content-type"] == "image/png"
        ), f"URL '{url}' returned non-image/png content-type: {response.headers['content-type']}"

        # name a note that we checked this URL (this time)
        self._checked_urls.add(url)

    def url_already_checked(self, url):
        """Check if the given URL has already been checked"""
        return url in self._checked_urls

    # pytest skip if we are NOT running in GitHub Actions
    @pytest.mark.skipif(not in_github_actions(), reason="Not running in GitHub Actions")
    def test_remote_images_by_id(self):
        """Test that the remote_image URLs are sane in character_by_id"""
        # all entries in character_by_id should have a remote_image key
        # and the URL should be a 200 response
        for role in self.json_data["character_by_id"].values():
            # key exists
            assert "remote_image" in role
            # we can assume we're running in github feature branches
            # if our branch is NOT main, then we need to replace 'main' in the URL
            # with our branch name
            branch = os.environ.get("GITHUB_HEAD_REF", "main")
            print(f"::notice::in github, working in branch: '{branch}'")
            remote_image_url = role["remote_image"].replace("main", branch)
            print(f"::notice::checking remote_image_url: '{remote_image_url}'")
            # URL looks sane
            self.remote_image_checks(remote_image_url)

    # pytest skip if we are NOT running in GitHub Actions
    @pytest.mark.skipif(not in_github_actions(), reason="Not running in GitHub Actions")
    def test_remote_images_role_list(self):
        """Test that the remote_image URLs are sane in role_list"""
        # all entries in role_list should have a remote_image key
        # and the URL should be a 200 response
        for role in self.json_data["role_list"]:
            # key exists
            assert "remote_image" in role
            # we can assume we're running in github feature branches
            # if our branch is NOT main, then we need to replace 'main' in the URL
            # with our branch name
            branch = os.environ.get("GITHUB_HEAD_REF", "main")
            print(f"::notice::in github, working in branch: '{branch}'")
            remote_image_url = role["remote_image"].replace("main", branch)
            print(f"::notice::checking remote_image_url: '{remote_image_url}'")

            # URL looks sane
            self.remote_image_checks(remote_image_url)
