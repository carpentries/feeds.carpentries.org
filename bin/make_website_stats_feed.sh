#!/bin/bash

## this script takes the path where the files will be generated as input

OUTPUT_PATH=$1

## Check that the API key is available
if [ -z "$REDASH_KEY_QUERY713" ]
then
    echo "The variable REDASH_KEY_QUERY713 is not set"
    exit 1
fi

REDASH_API_WEBSITE_STATS="https://redash.carpentries.org/api/queries/713/results.json?api_key=$REDASH_KEY_QUERY713"

## Store just the data from the query in a variable
data=$(curl "$REDASH_API_WEBSITE_STATS" | jq '.query_result.data.rows')

## Re-map the data keys/values
echo "$data" | jq 'map(select(.item != null) | {(.item): .item_count}) | add' > "$OUTPUT_PATH"/website_stats.json

