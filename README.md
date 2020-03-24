[![Build Status](https://travis-ci.com/carpentries/amy-feeds.svg?branch=master)](https://travis-ci.com/carpentries/amy-feeds)

# The Carpentries Data Feeds

This is a Jekyll repo for taking data from AMY and other sources and converting it to the JSON, GeoJSON and ICS formats used to show dynamic workshop and community member (trainers, instructors, maintainers, ...) data on The Carpentries websites.

## Usage 

**For data about The Carpentries workshops and community members:** If you want to run it locally, make sure you set the environment variable in the
shell for the Redash API key for [query
128](https://redash.carpentries.org/queries/128).

**For The Carpentries newsletter feed** be sure the Mailchimp API key is set.

Source JSON feeds are transformed using the [jq](https://stedolan.github.io/jq/) package.

**For data about The Carpentries lessons** make sure you have a Github PAT (Personal Authentication Token) set as an environment variable (`GITHUB_PAT`) with appropriate priviledges to read GitHub topics and issues for all our repositories.

You can then run the following command which will create all the feeds within
the `_site` folder.

```
make everything 
```

## Travis CI Deploy

Travis builds are triggered for this repo by a CRON job on the `build.carpentries.org` server. The files are are pushed to an S3 bucket and mapped (via CloudFlare CDN) to `https://feeds.carpentries.org/<pagename>`.

## Access Feeds

### JSON files

#### Workshops

*   [all\_instructors\_by\_airport.json](https://feeds.carpentries.org/all_instructors_by_airport.json)
*   [all\_past\_workshops.json](https://feeds.carpentries.org/all_past_workshops.json)
*   [all\_upcoming\_workshops.json](https://feeds.carpentries.org/all_upcoming_workshops.json)
*   [all\_workshops.json](https://feeds.carpentries.org/all_workshops.json)
*   [dc\_past\_workshops.json](https://feeds.carpentries.org/dc_past_workshops.json)
*   [dc\_upcoming\_workshops.json](https://feeds.carpentries.org/dc_upcoming_workshops.json)
*   [lc\_past\_workshops.json](https://feeds.carpentries.org/lc_past_workshops.json)
*   [lc\_upcoming\_workshops.json](https://feeds.carpentries.org/lc_upcoming_workshops.json)
*   [swc\_past\_workshops.json](https://feeds.carpentries.org/swc_past_workshops.json)
*   [swc\_upcoming\_workshops.json](https://feeds.carpentries.org/swc_upcoming_workshops.json)
*   [ttt\_past\_workshops.json](https://feeds.carpentries.org/ttt_past_workshops.json)
*   [ttt\_upcoming\_workshops.json](https://feeds.carpentries.org/ttt_upcoming_workshops.json)


#### Community members

*   [badges\_stats.json](https://feeds.carpentries.org/badges_stats.json)
*   [all\_badged\_people.json](https://feeds.carpentries.org/all_badged_people.json)
*   [dc\_instructors\_by\_airport.json](https://feeds.carpentries.org/dc_instructors_by_airport.json)
*   [lc\_instructors\_by\_airport.json](https://feeds.carpentries.org/lc_instructors_by_airport.json)
*   [swc\_instructors\_by\_airport.json](https://feeds.carpentries.org/swc_instructors_by_airport.json)

#### Lessons

* [lessons.json](https://feeds.carpentries.org/lessons.json)
* [community_lessons.md](https://feeds.carpentries.org/community_lessons.json)
* [help_wanted_issues.json](https://feeds.carpentries.org/help_wanted_issues.json)


#### Other data

* [newsletter.json](https://feeds.carpentries.org/newsletter.json)

### GeoJSON files

#### Workshops

*   [all\_workshops.geojson](https://feeds.carpentries.org/all_workshops.geojson)
*   [all\_workshops\_past.geojson](https://feeds.carpentries.org/all_workshops_past.geojson)
*   [dc\_workshops.geojson](https://feeds.carpentries.org/dc_workshops.geojson)
*   [dc\_workshops\_past.geojson](https://feeds.carpentries.org/dc_workshops_past.geojson)
*   [lc\_workshops.geojson](https://feeds.carpentries.org/lc_workshops.geojson)
*   [lc\_workshops\_past.geojson](https://feeds.carpentries.org/lc_workshops_past.geojson)
*   [swc\_workshops.geojson](https://feeds.carpentries.org/swc_workshops.geojson)
*   [swc\_workshops\_past.geojson](https://feeds.carpentries.org/swc_workshops_past.geojson)

#### Community members

*   [all\_instructors\_by\_airport.geojson](https://feeds.carpentries.org/all_instructors_by_airport.geojson)


## Adding new data feeds

New data feeds can be added by:

1. Including a script in [bin](/bin) to retrieve the JSON feed and send it to a file. For example: `"$OUTPUT_PATH"/newsletter.json`
1. Adding a rule in the [Makefile](Makefile) for that script and putting that rule under `everything`.
1. Adding the script from [bin](/bin) to the `before_script` section of [Travis](.travis.yml).
1. Adding the appropriate feed to the `/bin/update_feeds.sh` of the website repos that need it.


