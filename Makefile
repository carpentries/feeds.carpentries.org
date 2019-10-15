## everything : rebuild all data files and then the site
##   make sure `site` target is last in the list as it depends on all
##        the other ones
everything:
	@make workshops
	@make members
	@make newsletter
	@make plots
	@make incubator
	@make site


## workshops  : workshop JSON feeds from AMY data accessed from redash
workshops :
	./bin/make_workshop_feeds.sh _data/

## members    : feeds with information about our community members
members:
	./bin/make_members_feeds.sh _data/

## newsletter: pulls newsletters from Mailchip
newsletter:
	./bin/make_newsletter_feed.sh _data/

## plots: plot summaries
plots:
	R -q -e "source('R/workshop_summary.R')"
# 	python3 python/test.py
	python3 python/lesson_contributor_count.py
	python3 python/instructor_training_completion_rates.py


## incubator  : carpentries-incubator lesson feed
incubator:
	R -q -e "source('R/community_lessons.R')"

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
