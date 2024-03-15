# JSON on the Clocktower

![Version](https://img.shields.io/badge/latest-0.0.29-blue)

<!-- life's too short to worry about markdownlint in this file -->
<!-- markdownlint-disable MD013 -->
<!-- markdownlint-disable MD033 -->

This project is intended to be a simple-to-use, standalone, source of truth for
unofficial [Blood on the Clocktower][site-botc] tools.

While working on a separate project I quickly realised how much work I was
putting in to just get data shaped in a format that was easy (for me) to use.

## How to use

Grab a copy and save it to your project. Either commit it for fewer calls on
your part or just fetch every time!

### curl

Here's a quick way to grab the latest file:

```sh
curl \
  --silent \
  --create-dirs \
  -o data/imported/clocktower.json \
  https://raw.githubusercontent.com/chizmw/json-on-the-clocktower/main/data/generated/roles-combined.json
```

If you prefer to fetch a specific, fixed, set of data:

```sh
curl \
  --silent \
  --create-dirs \
  -o data/imported/clocktower.json \
  https://raw.githubusercontent.com/chizmw/json-on-the-clocktower/0.0.29/data/generated/roles-combined.json
```

### python

Here's the code I've been using myself:

```python

import json
import requests
import os

def external_data_filename() -> str:
    """Get the filename of the external data file."""
    return "data/imported/clocktower.json"


def ensure_data_exists():
    """Ensure the data exists."""
    # we should have data/generate/roles-combined.json
    # if we don't, we should fetch it from the remote source
    if not os.path.exists(external_data_filename()):
        # fetch the data
        file_data = fetch_remote_data(
            "https://raw.githubusercontent.com/chizmw/json-on-the-clocktower/"
            "main/data/generated/roles-combined.json"
        )

        # write it to the file
        with open(external_data_filename(), "w", encoding="utf-8") as json_file:
            json.dump(file_data, json_file, indent=4, sort_keys=True)
            # add a newline to the end of the file
            json_file.write("\n")
```

If you use poetry, install the dependencies:

```sh
poetry add requests
poetry add --group dev types-requests
```

## Getting to the information

I'll use `jq` to illustrate some parts of the information available.

To keep things a bit cleaner I used:

```sh
alias bloodq='cat data/imported/clocktower.json |jq'
```

### Top-level sections

```sh
❯ bloodq 'keys[]'
```

gives

```txt
"character_by_id"
"editions"
"jinxes"
"role_list"
"teams"
```

### Characters, as a list

```sh
bloodq '.role_list[]'
```

<details><summary>example output</summary>

Truncated after a couple of entries, because you get the idea:

```sh
# first three items for this sample output
bloodq '.role_list[:3]'
```

```json
[
  {
    "ability": "You start knowing that 1 of 2 players is a particular Townsfolk.",
    "edition": "tb",
    "firstNight": 33,
    "firstNightReminder": "Show the character token of a Townsfolk in play. Point to two players, one of which is that character.",
    "id": "washerwoman",
    "name": "Washerwoman",
    "otherNight": 0,
    "otherNightReminder": "",
    "reminders": ["Townsfolk", "Wrong"],
    "setup": false,
    "team": "townsfolk"
  },
  {
    "ability": "You start knowing that 1 of 2 players is a particular Outsider. (Or that zero are in play.)",
    "edition": "tb",
    "firstNight": 34,
    "firstNightReminder": "Show the character token of an Outsider in play. Point to two players, one of which is that character.",
    "id": "librarian",
    "name": "Librarian",
    "otherNight": 0,
    "otherNightReminder": "",
    "reminders": ["Outsider", "Wrong"],
    "setup": false,
    "team": "townsfolk"
  },
  {
    "ability": "You start knowing that 1 of 2 players is a particular Minion.",
    "edition": "tb",
    "firstNight": 35,
    "firstNightReminder": "Show the character token of a Minion in play. Point to two players, one of which is that character.",
    "id": "investigator",
    "name": "Investigator",
    "otherNight": 0,
    "otherNightReminder": "",
    "reminders": ["Minion", "Wrong"],
    "setup": false,
    "team": "townsfolk"
  }
]
```

</details>

### Information about a specific character, or meta role (e.g. demon night info)

```sh
bloodq '.character_by_id.empath'
```

<details><summary>example output</summary>

```json
{
  "ability": "Each night, you learn how many of your 2 alive neighbours are evil.",
  "edition": "tb",
  "firstNight": 36,
  "firstNightReminder": "Show the finger signal (0, 1, 2) for the number of evil alive neighbours of the Empath.",
  "id": "empath",
  "jinxes": [],
  "name": "Empath",
  "otherNight": 53,
  "otherNightReminder": "Show the finger signal (0, 1, 2) for the number of evil neighbours.",
  "reminders": [],
  "setup": false,
  "team": "townsfolk"
}
```

</details>

```sh
bloodq '.character_by_id.DEMON'
```

<details><summary>example output</summary>

```json
{
  "ability": "",
  "edition": "_meta",
  "firstNight": 8,
  "firstNightReminder": "If 7 or more players: wake up the Demon. Show the 'These are your minions' card. Point to each Minion. Show the 'These characters are not in play' card. Show 3 character tokens of Good characters that are not in play",
  "id": "DEMON",
  "jinxes": [],
  "name": "Demon Night Info",
  "otherNight": null,
  "otherNightReminder": "",
  "reminders": [],
  "setup": false,
  "team": "_meta"
}
```

</details>

### The known ids for roles

This includes the magical meta roles

```sh
bloodq -c '.character_by_id |keys[]'
```

<details><summary>example output</summary>
Limited to the first few items

```sh
bloodq -c '.character_by_id |keys[:7]'
```

```json
["DAWN", "DEMON", "DUSK", "MINION", "acrobat", "alchemist", "alhadikhia"]
```

[site-botc]: https://bloodontheclocktower.com
