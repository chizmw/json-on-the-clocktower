#!/usr/bin/env bash

# we can't rely on shell aliases to open `code-insiders` in preference to `code`
# so we'll crete a script function (code-open) to do that for us
code-open() {
    if [ -x "$(command -v code-insiders)" ]; then
        code-insiders "$@"
    else
        code "$@"
    fi
}

# the first argument is the new character slug (e.g. bootlegger)
# we should abort if this is missing
if [ -z "$1" ]; then
    echo "Please provide a character slug as the first argument"
    exit 1
else
    # the slug is the first argument
    SLUG=$1
fi

# if the second or third argument is force, set FORCE to true
if [ "$2" = "force" ] || [ "$3" = "force" ]; then
    FORCE=true
fi
# if the second or third argument is preserve, set PRESERVE to true
if [ "$2" = "preserve" ] || [ "$3" = "preserve" ]; then
    PRESERVE=true
fi

# make sure we don't already have a character with this slug
# i.e. data/extra-characters/{SLUG}.json should not exist
if [ -f "data/extra-characters/${SLUG}.json" ]; then
    if [ "$FORCE" = true ]; then
        echo "Removing existing character with the slug ${SLUG}"
        rm "data/extra-characters/${SLUG}.json"
    elif [ "$PRESERVE" = true ]; then
        echo "A character with the slug ${SLUG} already exists, but we continue"
    else
        echo "A character with the slug ${SLUG} already exists"
        exit 1
    fi
fi

# if we aren't using PRESERVE
if [ "$PRESERVE" != true ]; then
    # create the character file, a simple JSON object that's an empty array
    echo "[]" >"data/extra-characters/${SLUG}.json"
fi
code-open "data/extra-characters/${SLUG}.json"

# we have the edition file that contains the list of characters
# we need to add the new character to that list
# we'll use `jq` to do this
edition_file="data/role-edition.json"
# add '{"bootlegger": ""}' to the list of characters
jq --arg slug "$SLUG" '.[$slug] = ""' "$edition_file" >"$edition_file.tmp"
# overwrite the original file with the new file
mv "$edition_file.tmp" "$edition_file"

# commit our changes to the two files
git add "data/extra-characters/${SLUG}.json" "$edition_file"
git commit -m "feat: add ${SLUG} character"

# if our json is an empty list, we haven't added any character data
# so we should skip the rebuild and test steps
if [ "$(cat "data/extra-characters/${SLUG}.json")" = "[]" ]; then
    echo "No character data added, skipping rebuild and test steps"
    exit 0
fi

# the tests automatically include extra characters

# we should refresh our remote data
make rebuild-data

# and run the tests
make test
