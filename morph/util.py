""" Utility functions for the morph package. """

import logging
import json
import os
import requests


def fetch_remote_data(url: str):
    """Fetch data from a remote URL."""

    response = requests.get(url, timeout=10, allow_redirects=True)
    response.raise_for_status()
    return response.json()


def load_data(filename: str):
    """Load data from a JSON file."""
    with open(filename, encoding="utf-8") as fhandle:
        data = json.load(fhandle)
    return data


# we're outside the class now, and this is just helper functions
def cleanup_role_id(id_slug) -> str:
    """Cleanup the character ID."""

    # DO NOT change anything about these
    if id_slug in ["DEMON", "MINION", "DUSK", "DAWN"]:
        return id_slug

    # looking at other projects it seems that the ID in the (bra1n) script data is
    # _close_ to the ID in the role data
    # so we'll just do some cleanup to make it match
    # we do bra1n first, then clocktower.com because of the underscore removal
    id_slug = id_slug.replace("_", "")
    id_slug = id_slug.replace("-", "")  # just the pit-hag... why

    # data from clocktower.com doesn't match what we have in bra1n's data
    # so we'll just do some cleanup to make it match

    # remove all whitespace
    id_slug = id_slug.replace(" ", "")

    # remove all apostrophes
    id_slug = id_slug.replace("'", "")

    # lowercase
    id_slug = id_slug.lower()

    return id_slug


def configure_logger(logger_name: str) -> logging.Logger:
    """Configure the logger"""
    logger = logging.getLogger(logger_name)

    log_level = os.environ.get("LOGLEVEL", "INFO").upper()
    logger.setLevel(level=log_level)

    ch = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s [%(filename)s:%(lineno)s] %(levelname)s: %(message)s"
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.debug("Logging started for %s", logger.name)

    return logger
