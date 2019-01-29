PY=python3

amy :
	${PY} bin/get-amy.py -u https://amy.software-carpentry.org/api/v1/ -o _data/all_amy.yml --tags-any=SWC,DC,LC
	${PY} bin/get-amy.py -u https://amy.software-carpentry.org/api/v1/ -o _data/swc_amy.yml --tags-any=SWC
	${PY} bin/get-amy.py -u https://amy.software-carpentry.org/api/v1/ -o _data/dc_amy.yml --tags-any=DC
	${PY} bin/get-amy.py -u https://amy.software-carpentry.org/api/v1/ -o _data/lc_amy.yml --tags-any=LC


## workshops  : workshop JSON feeds from AMY data accessed from redash
workshops :
	./bin/make_workshop_feeds.sh _data/

## site       : build files but do not run a server.
## the files with the _plain suffix are created from the Redash query
## to make them available from the carpentries.org website we copy them
## to the `_site` folder
site :
	bundle exec jekyll build
	find _data -name '*_plain.json' -exec cp {} _site/ \;

## install    : install missing Ruby gems using bundle.
install :
	bundle install

## everything : rebuild all data files and then serve the site
everything:
	@make workshops
	@make amy
	@make site

#-------------------------------------------------------------------------------

## clean      : clean up junk files.
clean :
	rm -rf _site
