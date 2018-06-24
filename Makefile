PY=python3

amy :
	${PY} bin/get-amy.py -u https://amy.software-carpentry.org/api/v1/ -o _data/all_amy.yml --tags-any=SWC,DC,LC
	${PY} bin/get-amy.py -u https://amy.software-carpentry.org/api/v1/ -o _data/swc_amy.yml --tags-any=SWC
	${PY} bin/get-amy.py -u https://amy.software-carpentry.org/api/v1/ -o _data/dc_amy.yml --tags-any=DC
	${PY} bin/get-amy.py -u https://amy.software-carpentry.org/api/v1/ -o _data/lc_amy.yml --tags-any=LC


## site       : build files but do not run a server.
site :
	bundle exec jekyll build

## install    : install missing Ruby gems using bundle.
install :
	bundle install

## everything : rebuild all data files and then serve the site
everything:
	@make amy
	@make site

#-------------------------------------------------------------------------------

## clean      : clean up junk files.
clean :
	rm -rf _site
