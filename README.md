[![Build Status](https://travis-ci.com/carpentries/amy-feeds.svg?branch=master)](https://travis-ci.com/carpentries/amy-feeds)

# AMY Data Feeds

This is a Jekyll repo for taking YAML Data from AMY and converting it to the JSON, GeoJSON and ICS formats used to show dynamic workshop and instructor data on The Carpentries website.

## Usage 

Set environment variables in the shell for the Redash API key for [query 128](https://data.softwarecarpentry.org/queries/128):

```
make everything 
```

## Travis CI Deploy

Travis builds are triggered for this repo by a CRON job on the build.carpentries.org server. The files are are pushed to an S3 bucket and mapped (via CloudFlare CDN) to `https://feeds.carpentries.org/<pagename>`.

## Access Feeds

| File        | Description 
|------------|---------------|
| [all_instructors.json](https://feeds.carpentries.org/all_instructors.json) | GeoJSON - airport, list of names
| [dc_instructors.json](https://feeds.carpentries.org/dc_instructors.json) | GeoJSON - airport, list of names
| [lc_instructors.json](https://feeds.carpentries.org/lc_instructors.json) | GeoJSON - airport, list of names
| [dc_workshops.json](https://feeds.carpentries.org/dc_workshops.json) | GeoJSON - workshop location, html fragment
| [lc_workshops.json](https://feeds.carpentries.org/lc_workshops.json) | GeoJSON - workshop location, html fragment
| [dc_workshops_past.json](https://feeds.carpentries.org/dc_workshops_past.json) | GeoJSON - workshop location, html fragment
| [lc_workshops_past.json](https://feeds.carpentries.org/lc_workshops.json) | GeoJSON - workshop location, html fragment
| [swc_instructors.json](https://feeds.carpentries.org/swc_instructors.json) | GeoJSON - airport, list of names
| [swc_workshops.json](https://feeds.carpentries.org/swc_workshops.json) | GeoJSON - workshop location, html fragment
| [swc_workshops_past.json](https://feeds.carpentries.org/swc_workshops_past.json) | GeoJSON - workshop location, html fragment
| [workshops.json](https://feeds.carpentries.org/workshops.json) | GeoJSON  workshop location, html fragment
| [workshops_past.json](https://feeds.carpentries.org/workshops_past.json) | GeoJSON - workshop location, html fragment
| [all_workshops.ics](https://feeds.carpentries.org/all_workshops.ics) | GeoJSON - workshop location, html fragment
| [dc_workshops.ics](https://feeds.carpentries.org/dc_workshops.ics) | iCal - Calendar of workshops
| [swc_workshops.ics](https://feeds.carpentries.org/swc_workshops.ics) |iCal - Calendar of workshops
| [DC_past_workshops_plain.json](https://feeds.carpentries.org/DC_past_workshops_plain.json) | JSON of past DC workshops |
| [DC_upcoming_workshops_plain.json](https://feeds.carpentries.org/DC_upcoming_workshops_plain.json) | JSON of upcoming DC workshops |
| [LC_past_workshops_plain.json](https://feeds.carpentries.org/LC_past_workshops_plain.json) | JSON of past LC workshops |
| [LC_upcoming_workshops_plain.json](https://feeds.carpentries.org/LC_upcoming_workshops_plain.json) | JSON of upcoming LC workshops |
| [SWC_past_workshops_plain.json](https://feeds.carpentries.org/SWC_past_workshops_plain.json) | JSON of past SWC workshops |
| [SWC_upcoming_workshops_plain.json](https://feeds.carpentries.org/SWC_upcoming_workshops_plain.json) | JSON of upcoming SWC workshops |
| [TTT_past_workshops_plain.json](https://feeds.carpentries.org/TTT_past_workshops_plain.json) | JSON of past Instructor training workshops |
| [TTT_upcoming_workshops_plain.json](https://feeds.carpentries.org/TTT_upcoming_workshops_plain.json) | JSON of upcoming Instructor training workshops |
| [all_past_workshops_plain.json](https://feeds.carpentries.org/all_past_workshops_plain.json) | JSON of all past workshops since 2012 |
| [all_upcoming_workshops_plain.json](https://feeds.carpentries.org/all_upcoming_workshops_plain.json) | JSON of all upcoming workshops |
| [all_workshops_plain.json](https://feeds.carpentries.org/all_workshops_plain.json) | JSON of all workshops |


