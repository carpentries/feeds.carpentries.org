#!/bin/bash

shopt -s nullglob

echo "<!doctype html>" > _site/index.html
echo "<html lang=\"en\">" >> _site/index.html

echo "<head>" >> _site/index.html
echo "<meta charset=\"utf-8\">" >> _site/index.html
echo "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, shrink-to-fit=no\">" >> _site/index.html
echo "<title>List of The Carpentries Data Feeds</title>" >> _site/index.html
echo "<link rel=\"stylesheet\" href=\"https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css\" integrity=\"sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T\" crossorigin=\"anonymous\">" >> _site/index.html
echo "</head>" >> _site/index.html

echo "<body>" >> _site/index.html

echo "<div class=\"container\">" >> _site/index.html

echo "<h1>The Carpentries Data Feeds</h1>" >> _site/index.html

echo "<p class=\"lead\">" >> _site/index.html
echo "  The Carpentries provides a series of data feeds that we use" >> _site/index.html
echo "  to generate dynamic content on our websites. More information" >> _site/index.html
echo "  about these feeds are available in the" >> _site/index.html
echo "  <a href=\"https://github.com/carpentries/amy-feeds\">GitHub repository</a>." >> _site/index.html
echo "</p>" >> _site/index.html


echo "<h2>JSON files</h2>" >> _site/index.html
echo "<ul>" >> _site/index.html

for f in _site/*.json
do
    f="$(basename -- $f)"
    echo "<li><a href=\"$f\">$f</a></li>" >> _site/index.html
done

echo "</ul>" >> _site/index.html

echo "<h2>GeoJSON files</h2>" >> _site/index.html
echo "<ul>" >> _site/index.html

for f in _site/*.geojson
do
    f="$(basename -- $f)"
    echo "<li><a href=\"$f\">$f</a></li>" >> _site/index.html
done

echo "</ul>" >> _site/index.html

echo "</div>" >> _site/index.html

echo "</body>" >> _site/index.html
echo "</html>" >> _site/index.html
