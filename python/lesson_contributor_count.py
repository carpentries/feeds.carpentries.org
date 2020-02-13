import requests
import json
import os

token = os.environ['GITHUB_PAT']

ALL_ORG_REPOS = {'librarycarpentry': ['lc-data-intro', 'lc-shell', 'lc-open-refine', 'lc-git', 'lc-spreadsheets', 'lc-sql', 'lc-webscraping', 'lc-python-intro', 'lc-data-intro-archives'], 'carpentries': ['instructor-training'], 'swcarpentry': ['shell-novice', 'git-novice', 'python-novice-inflammation', 'python-novice-gapminder', 'r-novice-inflammation', 'r-novice-gapminder', 'shell-novice-es', 'git-novice-es', 'r-novice-gapminder-es', 'make-novice', 'matlab-novice-inflammation', 'sql-novice-survey', 'hg-novice'], 'datacarpentry': ['ecology-workshop', 'spreadsheet-ecology-lesson', 'OpenRefine-ecology-lesson', 'sql-ecology-lesson', 'R-ecology-lesson', 'python-ecology-lesson', 'python-ecology-lesson-es', 'genomics-workshop', 'organization-genomics', 'shell-genomics', 'wrangling-genomics', 'cloud-genomics', 'genomics-r-intro', 'socialsci-workshop', 'spreadsheets-socialsci', 'openrefine-socialsci', 'r-socialsci', 'python-socialsci', 'sql-socialsci', 'geospatial-workshop', 'organization-geospatial', 'r-intro-geospatial', 'r-raster-vector-geospatial']}

contributor_count = []

for lesson_program, lessons in ALL_ORG_REPOS.items():

    for lesson in lessons:
        repo = lesson_program + "/" + lesson

        contrib_count = 0
        
        for i in range(1, 10):
        
            CONTRIBS = "https://api.github.com/repos/" + repo + "/contributors?per_page=100&page=" + str(i)
            r = requests.get(url=CONTRIBS, auth=('fmichonneau', token))
            contrib_count += len(r.json())
            if len(r.json()) == 0:
                break

        contributor_count.append({'lesson':lesson, 'lesson_program':lesson_program, 'contributor_count':contrib_count})

with open('./lesson_contributor_count.json', 'w') as fp:
    json.dump(contributor_count, fp)




