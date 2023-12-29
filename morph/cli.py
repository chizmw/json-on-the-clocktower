""" Turn all the JSON data into One-JSON-To-Rule-Them-All"""

import click

from morph.json.incoming import JsonIncoming
from morph.json.onetruejson import OneTrueJson


@click.command()  # type: ignore
@click.option("--force-fetch", is_flag=True, help="Force fetch of data from the web")
def combiner(force_fetch):
    """Turn all the JSON data into One-JSON-To-Rule-Them-All"""

    # create a new JsonIncoming object
    incoming = JsonIncoming(force_fetch=force_fetch)

    # create a new OneTrueJson object
    one_true_json = OneTrueJson(incoming)

    # write the data to a file
    one_true_json.write("data/generated/roles-combined-v3.json")
    one_true_json.write("data/generated/roles-combined.json")


if __name__ == "__main__":
    combiner(None)  # type: ignore
