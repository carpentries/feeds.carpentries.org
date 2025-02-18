## everything : rebuild all data files and then the site
##   make sure `site` target is last in the list as it depends on all
##        the other ones
everything:
	@make workshops
	@make members
	@make amy_curricula
	@make newsletter
	@make plots
	@make incubator
	@make help-wanted
	@make lessons
	@make memberships
	@make website_stats
	@make site

## website_stats : quick stats for bubbles on website
website_stats:
	./bin/make_website_stats_feed.sh _data/

## workshops  : workshop JSON feeds from AMY data accessed from redash
workshops :
	./bin/make_workshop_feeds.sh _data/
	python3 python/workshop_stats.py

## members    : feeds with information about our community members
members:
	./bin/make_members_feeds.sh _data/
	./bin/make_active_roles.sh _data/

## amy_curricula  : feeds with information about our curricula as recorded in AMY
amy_curricula:
	./bin/make_amy_curricula.sh _data/

## newsletter: pulls newsletters from Mailchip
newsletter:
	./bin/make_newsletter_feed.sh _data/

## memberships
memberships:
	./bin/make_membership_feed.sh _data/

## plots: plot summaries
plots:
	R -q -e "source('R/workshop_summary.R')"
	python3 python/lesson_contributor_count.py
	python3 python/instructor_training_completion_rates.py
	# Drop seat usage feed/plot for now - does not work well 
	# python3 python/instructor_training_seat_usage.py 
	# Drop curriculum frequency for now - needs to be updated 
	# python3 python/curriculum_teaching_frequency.py
	python3 python/instructor_teaching_frequency.py
	python3 python/checkout_steps.py
	python3 python/membership_trends.py


## incubator  : carpentries-incubator lesson feed
incubator:
	R -q -e "source('R/community_lessons.R')"

## help-wanted: list of issues that have the label "help wanted"
help-wanted:
	R -q -e "source('R/help_wanted_issues.R')"

## lessons    : data feed for the repository information for all "official" lessons
lessons:
	R -q -e "source('R/curriculum_feed.R')"

## site       : build files but do not run a server.
## some files created from the Redash query need to be copied to the
## `_site` folder to make them publicly available.
site :
	bundle exec jekyll build
	find _data -name '*.json' -exec cp {} _site/ \;
	find _images -iregex ".*.\(svg\|html\|png\|jpg\|jpeg\)" -exec cp {} _site/ \;
	./bin/make_index.sh

## install    : install missing Ruby gems using bundle.
install :
	bundle install

#-------------------------------------------------------------------------------

## clean      : clean up junk files.
clean :
	rm -rf _site
