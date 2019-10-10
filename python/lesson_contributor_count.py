
import requests
import json
import os

token = os.environ['GITHUB_PAT']

ALL_ORG_REPOS = ["datacarpentry/ecology-workshop", "datacarpentry/spreadsheet-ecology-lesson", "datacarpentry/OpenRefine-ecology-lesson", "datacarpentry/sql-ecology-lesson", "datacarpentry/R-ecology-lesson", "datacarpentry/python-ecology-lesson", "datacarpentry/python-ecology-lesson-es", "datacarpentry/genomics-workshop", "datacarpentry/organization-genomics", "datacarpentry/shell-genomics", "datacarpentry/wrangling-genomics", "datacarpentry/cloud-genomics", "datacarpentry/genomics-r-intro", "datacarpentry/socialsci-workshop", "datacarpentry/spreadsheets-socialsci", "datacarpentry/openrefine-socialsci", "datacarpentry/r-socialsci", "datacarpentry/python-socialsci", "datacarpentry/sql-socialsci", "datacarpentry/geospatial-workshop", "datacarpentry/organization-geospatial", "datacarpentry/r-intro-geospatial", "datacarpentry/r-raster-vector-geospatial", "carpentries/instructor-training", "swcarpentry/shell-novice", "swcarpentry/git-novice", "swcarpentry/python-novice-inflammation", "swcarpentry/python-novice-gapminder", "swcarpentry/r-novice-inflammation", "swcarpentry/r-novice-gapminder", "swcarpentry/shell-novice-es", "swcarpentry/git-novice-es", "swcarpentry/r-novice-gapminder-es", "swcarpentry/make-novice", "swcarpentry/matlab-novice-inflammation", "swcarpentry/sql-novice-survey", "swcarpentry/hg-novice", "librarycarpentry/lc-data-intro", "librarycarpentry/lc-shell", "librarycarpentry/lc-open-refine", "librarycarpentry/lc-git", "librarycarpentry/lc-spreadsheets", "librarycarpentry/lc-sql", "librarycarpentry/lc-webscraping", "librarycarpentry/lc-python-intro", "librarycarpentry/lc-data-intro-archives",]

contributor_count = []

for repo in ALL_ORG_REPOS:
    
    contrib_count = 0
    
    for i in range(1, 10):
    
        CONTRIBS = "https://api.github.com/repos/" + repo + "/contributors?per_page=100&page=" + str(i) + "&access_token=" + token
        r = requests.get(url=CONTRIBS)
        contrib_count += len(r.json())
        if len(r.json()) == 0:
            break

    contributor_count.append({'lesson':repo, 'contributor_count':contrib_count})

with open('./lesson_contributor_count.json', 'w') as fp:
    json.dump(contributor_count, fp)


