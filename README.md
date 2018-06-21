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

* [all_instructors.json](https://s3.amazonaws.com/amydata.carpentries.org/all_instructors.json)
* [dc_instructors.json](https://s3.amazonaws.com/amydata.carpentries.org/dc_instructors.json
* [dc_workshops.json](https://s3.amazonaws.com/amydata.carpentries.org/dc_workshops.json)
* [dc_workshops_past.json](https://s3.amazonaws.com/amydata.carpentries.org/dc_workshops_past.json)
* [swc_instructors.json](https://s3.amazonaws.com/amydata.carpentries.org/swc_instructors.json)
* [swc_workshops.json](https://s3.amazonaws.com/amydata.carpentries.org/swc_workshops.json)
* [swc_workshops_past.json](https://s3.amazonaws.com/amydata.carpentries.org/swc_workshops_past.json]
* [workshops.json](https://s3.amazonaws.com/amydata.carpentries.org/workshops.json)
* [workshops_past.json](https://s3.amazonaws.com/amydata.carpentries.org/workshops_past.json)


