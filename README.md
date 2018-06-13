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

