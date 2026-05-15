#!/bin/bash

## this script takes the path where the files will be generated as input

OUTPUT_PATH=$1


## Check that the API key is available
if [ -z "$REDASH_KEY_QUERY803" ]
then
    echo "The variable REDASH_KEY_QUERY803 is not set"
    exit 1
fi

REDASH_API_PARTNERSHIPS="https://redash.carpentries.org/api/queries/803/results.json?api_key=$REDASH_KEY_QUERY803"


## ALL members ---------------------------------------------------------------

curl "$REDASH_API_PARTNERSHIPS" | jq '
     .query_result.data.rows 
' > "$OUTPUT_PATH"/all_public_partnerships.json
