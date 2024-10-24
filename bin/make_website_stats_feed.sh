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
response=$(curl -s -w "%{http_code}" "$REDASH_API_WEBSITE_STATS")
status_code=${response: -3}  # last 3 characters (HTTP status code)
json_body=$(curl $REDASH_API_WEBSITE_STATS)


## Make sure status code is 200
if [ "$status_code" -ne 200 ]; then
    echo "Error: Unable to reach the API or invalid response. HTTP status code: $status_code"
    exit 1
fi

## Make sure data is not empty
if [ -z "$json_body" ]
then
    echo "The variable REDASH_KEY_QUERY713 is not set"
    exit 1
fi

## Make sure the returned data contains query_result

if echo "$json_body" | jq -e 'has("query_result")'; then
    echo "$json_body" | jq '.query_result.data.rows'
    data=$(curl "$REDASH_API_WEBSITE_STATS" | jq '.query_result.data.rows')
    echo "$data" | jq 'map(select(.item != null) | {(.item): .item_count}) | add' > "$OUTPUT_PATH"/website_stats.json
else
    echo "Error: the requested data is invalid."
    exit 1
fi



