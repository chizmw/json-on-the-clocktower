""" Tests to ensure some basic generated file sanity """

import json
import logging
import os

import pytest
import requests

LOGGER = logging.getLogger(__name__)


def in_github_actions():
    """Check if we're running in GitHub Actions"""
    return os.environ.get("GITHUB_ACTIONS", "false") == "true"


class TestJsonData:
    """Tests for the contents of the generated JSON data."""

    _branch: str = os.environ.get("GITHUB_HEAD_REF", "main")
    _data_file: str = "data/generated/roles-combined.json"
    _json_data: dict = {}
    _checked_urls: set = set()

    @property
    def _git_branch(self) -> str:
        """Return the name of the git branch we're running in"""
        return self._branch

    @property
    def data_file(self) -> str:
        """Return the name of the data file we're testing"""
        return self._data_file

    @property
    def json_data(self) -> dict:
        """Return the JSON data we're testing"""
        return self._json_data

    @json_data.setter
    def json_data(self, value: dict) -> None:
        """Set the JSON data we're testing"""
        self._json_data = value

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup our 'self' for each test"""
        # make sure our data file exists
        assert os.path.exists(str(self.data_file))
        # load the data file
        assert self.json_data is not None
        with open(str(self.data_file), "r", encoding="utf-8") as data_file:
            # load the data
            self.json_data = json.load(data_file)
        # check the data is loaded
        assert self.json_data is not None
        # clear the checked URLs
        self._checked_urls = set()

        # we should never have an empty value for the git branch
        assert self._git_branch is not None
        assert self._git_branch != ""

    def test_top_level_keys(self):
        """Test that the top-level keys in the data file are as expected."""

        # check that the keys are as expected
        assert set(self.json_data.keys()) == set(
            [
                "character_by_id",
                "editions",
                "jinxes",
                "roles",
                "teams",
            ]
        )

    def test_missing_info(self):
        """Make sure we have all the info we need for each role in the expected places"""

        # for the id of each  role in the role_list, we should have a
        # corresponding entry in character_by_id
        for role_id in self.json_data["roles"]:
            # the role-id should be a string
            assert isinstance(role_id, str)
            # it should exist in character_by_id
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
            remote_image_url = role["remote_image"]
            if not self._on_default_branch():
                branch = self._git_branch
                # assert that the branch is not None, and also not empty
                assert branch is not None
                assert branch != ""
                LOGGER.info("in github, working in non-default branch: '%s'", branch)
                remote_image_url = role["remote_image"].replace("main", branch)
            # URL looks sane
            self.remote_image_checks(remote_image_url)

    def _on_default_branch(self) -> bool:
        """Check if we're on the default branch"""
        return self._git_branch == "main"
