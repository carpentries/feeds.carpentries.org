#!/bin/bash

## this script takes the path where the files will be generated as input

OUTPUT_PATH=$1

REDASH_API_WORKSHOPS="https://data.softwarecarpentry.org/api/queries/125/results.json?api_key=ef7xp02JqDvg7JkEbxbElfg8ICgBaQEaXnz0NhQS"

CARPENTRIES_PROGRAMS=('SWC' 'DC' 'LC' 'TTT')

## ALL workshops ---------------------------------------------------------------

curl "$REDASH_API_WORKSHOPS" | jq '.query_result.data.rows' > "$OUTPUT_PATH"/all_workshops_plain.json

## Past workshops --------------------------------------------------------------

## all
jq 'map(select(.end_date | strptime("%Y-%m-%d")? | mktime < now)) | sort_by(.start_date | strptime("%Y-%m-%d")? | mktime | reverse)' < "$OUTPUT_PATH"/all_workshops.json > "$OUTPUT_PATH"/all_past_workshops_plain.json

## for each program
for prgm in "${CARPENTRIES_PROGRAMS[@]}"; do
    jq "map(select(.tag_name == \"$prgm\"))" < "$OUTPUT_PATH"/all_past_workshops.json > "$OUTPUT_PATH"/"$prgm"_past_workshops_plain.json
done


## Upcoming workshops ----------------------------------------------------------

## all
jq 'map(select(.end_date | strptime("%Y-%m-%d")? | mktime >= now)) | sort_by(.start_date | strptime("%Y-%m-%d")? | mktime)' < "$OUTPUT_PATH"/all_workshops.json > "$OUTPUT_PATH"/all_upcoming_workshops_plain.json

## for each program
for prgm in "${CARPENTRIES_PROGRAMS[@]}"; do
    jq "map(select(.tag_name == \"$prgm\"))" < "$OUTPUT_PATH"/all_upcoming_workshops.json > "$OUTPUT_PATH"/"$prgm"_upcoming_workshops_plain.json
done
