#!/bin/bash

shopt -s nullglob

echo "<!doctype html>" > _site/full_list.html
echo "<html lang=\"en\">" >> _site/full_list.html

echo "<head>" >> _site/full_list.html
echo "<meta charset=\"utf-8\">" >> _site/full_list.html
echo "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, shrink-to-fit=no\">" >> _site/full_list.html
echo "<title>List of The Carpentries Data Feeds</title>" >> _site/full_list.html
echo "<link rel=\"stylesheet\" href=\"https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css\" integrity=\"sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T\" crossorigin=\"anonymous\">" >> _site/full_list.html
echo "</head>" >> _site/full_list.html

echo "<body>" >> _site/full_list.html

echo "<div class=\"container\">" >> _site/full_list.html

echo "<h1>The Carpentries Data Feeds</h1>" >> _site/full_list.html

echo "<p class=\"lead\">" >> _site/full_list.html
echo "  The Carpentries provides a series of data feeds that we use" >> _site/full_list.html
echo "  to generate dynamic content on our websites. More information" >> _site/full_list.html
echo "  about these feeds are available in the" >> _site/full_list.html
echo "  <a href=\"https://github.com/carpentries/amy-feeds\">GitHub repository</a>." >> _site/full_list.html
echo "</p>" >> _site/full_list.html

## Plots

echo "<h2>Plots</h2>" >> _site/full_list.html
echo "<ul>" >> _site/full_list.html

for f in _site/plot_*.{html,svg}
do
    f="$(basename -- $f)"
    echo "<li><a href=\"$f\">$f</a></li>" >> _site/full_list.html
done

echo "</ul>" >> _site/full_list.html

## JSON files

echo "<h2>JSON files</h2>" >> _site/full_list.html
echo "<ul>" >> _site/full_list.html

for f in _site/*.json
do
    f="$(basename -- $f)"
    echo "<li><a href=\"$f\">$f</a></li>" >> _site/full_list.html
done

echo "</ul>" >> _site/full_list.html

## JSON files

echo "<h2>GeoJSON files</h2>" >> _site/full_list.html
echo "<ul>" >> _site/full_list.html

for f in _site/*.geojson
do
    f="$(basename -- $f)"
    echo "<li><a href=\"$f\">$f</a></li>" >> _site/full_list.html
done

echo "</ul>" >> _site/full_list.html

echo "<small>Last updated $(date)</small>" >> _site/full_list.html

echo "</div>" >> _site/full_list.html

echo "</body>" >> _site/full_list.html
echo "</html>" >> _site/full_list.html
