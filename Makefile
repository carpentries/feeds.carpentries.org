## everything : rebuild all data files and then the site
everything:
	@make workshops
	@make members
	@make site


## workshops  : workshop JSON feeds from AMY data accessed from redash
workshops :
	./bin/make_workshop_feeds.sh _data/

## members    : feeds with information about our community members
members:
	./bin/make_members_feeds.sh _data/

## site       : build files but do not run a server.
## some files created from the Redash query need to be copied to the
## `_site` folder to make them publicly available.
site :
	bundle exec jekyll build
	find _data -name '*.json' -exec cp {} _site/ \;
	./bin/make_index.sh

## install    : install missing Ruby gems using bundle.
install :
	bundle install

#-------------------------------------------------------------------------------

## clean      : clean up junk files.
clean :
	rm -rf _site
