#!/bin/bash

## To avoid having to export the API key every time you run the script
## you can store it in a file called 'api_key.sh'. It will only be sourced
## locally as the environment variable "CI" is set on Travis.
if [ -z "$CI" ]
then
    echo "not on Travis sourcing locally stored API key"
    source api_key.sh
fi

OUTPUT_PATH=$1

## Check that the API key is available
if [ -z "$REDASH_API_INSTRUCTORS_KEY" ]
then
    echo "The variable REDASH_API_INSTRUCTORS_KEY is not set"
    exit 1
fi


## Download the file from Redash
REDASH_API_INSTRUCTORS="https://data.softwarecarpentry.org/api/queries/128/results.json?api_key=$REDASH_API_INSTRUCTORS_KEY"

curl "$REDASH_API_INSTRUCTORS" |
    jq '.query_result.data.rows |
    map(
   .is_maintainer =  contains({badges: "6"}) |
   .is_swc_instructor = contains({badges: "2"}) |
   .is_dc_instructor = contains({badges: "5"}) |
   .is_lc_instructor = contains({badges: "10"}) |
   .is_trainer = contains({badges: "7"}) |
   .is_mentor = contains({badges: "8"})
   )' > "$OUTPUT_PATH"/instructors_raw.json

## Make sure the file was successfully downloaded
if [ ! -s "$OUTPUT_PATH"/instructors_raw.json ]
then
    echo "Couldn't get data from Redash server."
    exit 1
fi

## statistics
jq '{
  n_maintainers: map(select(.is_maintainer)) | length,
  n_trainers: map(select(.is_trainer)) | length,
  n_instructors: map(select(
      .is_swc_instructor or .is_dc_instructor or
      .is_lc_instructor
  )) | length,
  n_swc_instructors: map(select(.is_swc_instructor)) | length,
  n_dc_instructors:  map(select(.is_dc_instructor)) | length,
  n_lc_instructors:  map(select(.is_lc_instructor)) | length,
  n_mentors:         map(select(.is_mentor))  | length,
  instructors_by_country: map(
    select(
       .country != "" and
      (.is_swc_instructor or .is_lc_instructor or .is_dc_instructor)
    )) |
    group_by(.country) |
    map(
      { (.[].country): . | length }
    ) | unique ,
  dc_instructors_by_country: map(
    select(
     .country != "" and .is_dc_instructor
    )) |
    group_by(.country) |
    map(
      { (.[].country): . | length }
    ) | unique,
  lc_instructors_by_country: map(
    select(
     .country != "" and .is_lc_instructor
    )) |
    group_by(.country) |
    map(
      { (.[].country): . | length }
    ) | unique,
  swc_instructors_by_country: map(
    select(
     .country != "" and .is_swc_instructor
    )) |
    group_by(.country) |
    map(
      { (.[].country): . | length }
    ) | unique,
  trainers_by_country: map(
      select(
     .country != "" and .is_trainer
    )) |
    group_by(.country) |
    map(
      { (.[].country): . | length }
    ) | unique,
  maintainers_by_country: map(
      select(
     .country != "" and .is_maintainer
    )) |
    group_by(.country) |
    map(
      { (.[].country): . | length }
    ) | unique
}
' < "$OUTPUT_PATH"/instructors_raw.json > "$OUTPUT_PATH"/badges_stats.json


## anonymized feed with airport information
jq '
   map(select(.publish_profile == 1)) |
  .[].person_name_with_middle |= (. | gsub("(\\b(?<fl>[A-Za-z]{1})\\w*)";"\(.fl)") |
   gsub("[^A-Za-z]"; "")) |
   group_by(.iata) |
   map(
     reduce .[] as $x(.[0] | del (.person_name_with_middle);
     .people += [ $x.person_name_with_middle ])
   ) |
   map(
      del(
        .person_name, .person_email, .publish_profile,
        .github, .url, .country, .twitter, .orcid,
        .badges
         )
   ) |
   map(
     {
       airport_code: .iata,
       airport_latitude: .latitude,
       airport_longitude: .longitude,
       instructors: .people
     }
   )
' < "$OUTPUT_PATH"/instructors_raw.json > "$OUTPUT_PATH"/amy_airports.json

###  Feed for instructor page

## We add http:// in from of URLs if it's missing
## We remove potential URL prefix in ORCID field
## We remove potential '@' in front of twitter handle
## We make sure the email are all lower case to get the correct MD5 hash

jq '
   map(select(.publish_profile == 1)) |
   map(
   .url |= if ((. | length) == 0 or test("^https?"))
               then . else "http://" + . end |
   .orcid   |= if (. != null) then . | split("/") | last else . end |
   .twitter |= if (. != null) then . | gsub("^@";  "") else . end |
   .person_email |= if (. != null) then . | ascii_downcase else . end |
   del(.publish_profile)
)' < "$OUTPUT_PATH"/instructors_raw.json > /tmp/instructors_clean.json


jq -c '.[]' < /tmp/instructors_clean.json |
    while read -r line;
    do
        email=$(jq -r '[.person_email]|add' <<< "$line")
        echo -n "$email"                                     |
            md5sum  |
            cut -d ' ' -f1 |
            jq --argjson line "$line" -R '$line  + {gravatar: .}'
    done  |
    jq -s '
          map(del (
            .person_name_with_middle,
            .iata, .latitude, .longitude,
            .person_email
          ))
    '> "$OUTPUT_PATH"/publish_instructors.json


rm /tmp/instructors_clean.json
