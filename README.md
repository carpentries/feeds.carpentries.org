![build and deploy data feeds](https://github.com/carpentries/feeds.carpentries.org/workflows/build%20and%20deploy%20data%20feeds/badge.svg)

# The Carpentries Data Feeds

This is a Jekyll repo for taking data from AMY and other sources and converting it to the JSON, GeoJSON and ICS formats used to show dynamic workshop and community member (trainers, instructors, maintainers, ...) data on The Carpentries websites.

Source JSON feeds are transformed using the [jq](https://stedolan.github.io/jq/)
package.

The Makefile calls for scripts written in R and Python.

## Usage 

**For data about The Carpentries workshops and community members:** If you want to run it locally, make sure you set the environment variable in the
shell for all the Redash API keys for all the queries used.

**For The Carpentries newsletter feed** be sure the Mailchimp API key is set.

**For data about The Carpentries lessons** make sure you have a Github PAT (Personal Authentication Token) set as an environment variable (`GITHUB_PAT`) with appropriate priviledges to read GitHub topics and issues for all our repositories.

You can then run the following command which will create all the feeds within
the `_site` folder.

```
make everything 
```

## GitHub Actions Deployment

A GitHub Action runs every 6 hours (at 0, 6am, noon, 6pm UTC) to retrieve the build the data feeds.

## Adding new data feeds

New data feeds can be added by:

1. Including a script in [bin](/bin) to retrieve the JSON feed and send it to a file. For example: `"$OUTPUT_PATH"/newsletter.json`
1. Adding a rule in the [Makefile](Makefile) for that script and putting that rule under `everything`.
1. Adding the script from [bin](/bin) to the `before_script` section of [Travis](.travis.yml).
1. Adding the appropriate feed to the `/bin/update_feeds.sh` of the website repos that need it.


