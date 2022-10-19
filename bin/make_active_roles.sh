#!/bin/bash

## this script takes the path where the files will be generated as input

OUTPUT_PATH=$1


## Check that the API key is available
if [ -z "$REDASH_KEY_QUERY523" ]
then
    echo "The variable REDASH_KEY_QUERY523 is not set"
    exit 1
fi

REDASH_API_TRAINERS="https://redash.carpentries.org/api/queries/523/results.json?api_key=$REDASH_KEY_QUERY523"


## ALL Trainers  ---------------------------------------------------------------

curl "$REDASH_API_TRAINERS" | jq '
     .query_result.data.rows 
' > "$OUTPUT_PATH"/all_trainers.json



## Check that the API key is available
if [ -z "$REDASH_KEY_QUERY524" ]
then
    echo "The variable REDASH_KEY_QUERY524 is not set"
    exit 1
fi

REDASH_API_MAINTAINERS="https://redash.carpentries.org/api/queries/524/results.json?api_key=$REDASH_KEY_QUERY524"


## ALL Trainers  ---------------------------------------------------------------

curl "$REDASH_API_MAINTAINERS" | jq '
     .query_result.data.rows 
' > "$OUTPUT_PATH"/all_maintainers.json
