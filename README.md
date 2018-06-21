# AMY Data Feeds

This is a Jekyll repo for taking YAML Data from AMY and converting it to the JSON and GeoJSON formats used to show workshop and instructor data on The Carpentries website.

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

This repo is used to dynamically update AMY instructor profiles. Travis is set to rebuild from the AMY instructor database once per day.

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


