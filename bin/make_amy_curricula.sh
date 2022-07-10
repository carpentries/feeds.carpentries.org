#!/bin/bash

## this script takes the path where the files will be generated as input

OUTPUT_PATH=$1

REDASH_API_CURRICULA="https://redash.carpentries.org/api/queries/144/results.json?api_key=LJq4DvcsHXFK5twwp97yXeSB2eSpqnYZydIPQP2E"

## AMY Curricula ---------------------------------------------------------------

curl "$REDASH_API_CURRICULA" | jq '
     .query_result.data.rows |
     map({name, slug, description, carpentry, active, mix_match})
' > "$OUTPUT_PATH"/amy_curricula.json
