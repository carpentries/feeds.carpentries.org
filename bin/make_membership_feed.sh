#!/bin/bash

## this script takes the path where the files will be generated as input

OUTPUT_PATH=$1

REDASH_API_MEMBERSHIPS="https://redash.carpentries.org/api/queries/400/results.json?api_key=1234567"



## ALL members ---------------------------------------------------------------

curl "$REDASH_API_MEMBERSHIPS" | jq '
     .query_result.data.rows 
' > "$OUTPUT_PATH"/all_public_memberships.json
