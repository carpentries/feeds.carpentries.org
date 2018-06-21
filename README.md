# AMY Data Feeds

This is a Jekyll repo for taking YAML Data from AMY and converting it to the JSON, GeoJSON and ICS formats used to show dynamic workshop and instructor data on The Carpentries website.

## Usage 

Set environment variables in the shell for AMY authentication:
```
export AMY_USER="XXXX"
export AMY_PASS="XXXX"
```

```
make amy
make site 
```

## Travis CI Deploy

This repo is used to dynamically update AMY instructor profiles. Travis is set to rebuild from the AMY instructor database once per day. Then the built feeds are pushed to an S3 bucket and mapped (via CloudFlare CDN) to `https://carpentries.org/amy/<pagename>`

## Access Feeds

* [all_instructors.json](https://carpentries.org/amy/all_instructors.json)
* [dc_instructors.json](https://carpentries.org/amy/dc_instructors.json)
* [dc_workshops.json](https://carpentries.org/amy/dc_workshops.json)
* [dc_workshops_past.json](https://carpentries.org/amy/dc_workshops_past.json)
* [swc_instructors.json](https://carpentries.org/amy/swc_instructors.json)
* [swc_workshops.json](https://carpentries.org/amy/swc_workshops.json)
* [swc_workshops_past.json](https://carpentries.org/amy/swc_workshops_past.json)
* [workshops.json](https://carpentries.org/amy/workshops.json)
* [workshops_past.json](https://carpentries.org/amy/workshops_past.json)
* [all_workshops.ics](https://carpentries.org/amy/all_workshops.ics)
* [dc_workshops.ics](https://carpentries.org/amy/dc_workshops.ics)
* [swc_workshops.ics](https://carpentries.org/amy/swc_workshops.ics)


