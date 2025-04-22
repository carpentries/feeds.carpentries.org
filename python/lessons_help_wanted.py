# Import all the things
import requests
import os
from datetime import datetime
import time
import json

# Set global vars
GH_ORG_DC = "datacarpentry"
GH_ORG_SWC = "swcarpentry"
GH_ORG_LC = "librarycarpentry"
GH_ORG_LAB = "carpentries-lab"
GH_ORG_INC = "carpentries-incubator"
ALL_ORGS = [GH_ORG_DC, GH_ORG_LC, GH_ORG_SWC, GH_ORG_LAB, GH_ORG_INC,]
GH_SEARCH_BASE_URL = "https://api.github.com/search"
GH_ORG_BASE_URL = "https://api.github.com/orgs"

topics = "stable,helpwanted-list"
labels = "\"help wanted\",\"good first issue\""

# Authentication
GH_TOKEN = os.environ['GITHUB_PAT_HELPWANTED']

headers = {
    "Authorization": f"token {GH_TOKEN}",
    "Accept": "application/vnd.github+json"
}


def get_json(url, headers, params=None):
    """
    Function takes
    * GH API url as string
    * Authentication headers as dict
    * Optional params to pass to API call
    Returns the retrieved json or error message
    """
    r = requests.get(url, headers=headers, params=params)
    if r.status_code != 200:
        print(f"Failed to retrieve data: {r.status_code}, {r.json()}")
        return r.status_code
    return r.json()


def get_repos_by_topic(org, repo_topics):
    """
    Function takes:
    * GH organization name as a string (eg "swcarpentry" or "carpentries")
    * GH repo topics to search for as a csv string.
    Queries for all GH repos in that organization that have the topic "stable".
    Returns list of dicts with repo and org data (to be used to gather help-wanted issues in that repo).
    """

    print(f"Searching for repos in {org} with topics: {topics}")
    # Get GH organization name and url
    org_url = f"{GH_ORG_BASE_URL}/{org}"

    gh_org = get_json(org_url, headers)

    if 'name' in gh_org:
        org_full_name = gh_org['name']
    else:
        print("Key 'name' not found.")
        return gh_org

    if 'html_url' in gh_org:
        org_url = gh_org['html_url']
    else:
        print("Key 'html_url' not found.")
        return gh_org

    # Get all repos in that organization the topic "stable"
    # Additional topics can be added separated by commas and use OR logic.
    params = {
        "q": f"org:{org} topic:{repo_topics}",
    }

    repos_with_topic_req = get_json(f"{GH_SEARCH_BASE_URL}/repositories", headers, params)

    # repos_with_topic = repos_with_topic_req.json()['items']
    if 'items' in repos_with_topic_req:
        repos_with_topic = repos_with_topic_req['items']
    else:
        print("Key 'items' not found.")
        return repos_with_topic_req

    # Build list of dicts
    # This will be used as base dict for each repo
    repos_with_topic_clean = [{"repo_url": repo["html_url"],
                               "repo_description": repo["description"],
                               "repo_name": repo["name"],
                               "org_name": org,
                               "org_full_name": org_full_name,
                               "org_url": org_url} for repo in repos_with_topic]
    count_repos = len(repos_with_topic_clean)
    print(f"Found {count_repos} repos.")
    return repos_with_topic_clean


def get_help_wanted_issues(repos_with_topic, issue_labels):
    """
    Function takes:
    * list of dicts created by get_repos_by_topic()
    * GH issue labels to search for as a csv string. Issue names with whitespace
    must be surrounded by escaped double quotes.

    Iterates over each dict to search for all issues in that repo with those labels.
    Returns list of issues with those tags identified by repo & organization.
    """

    # Rough hacky check on if `repos_with_topic` is non-zero length and properly formatted list of dicts
    if len(repos_with_topic) == 0:
        print("Empty data for 'repos_with_topic'")
        return
    if not isinstance(repos_with_topic, list) or "org_url" not in repos_with_topic[0].keys():
        print("Invalid source data for repos_with_topic")
        return

    print(f"Searching for issues with labels: {issue_labels}")
    # Initialize empty list to store list of dicts for each issue
    all_help_wanted_issues = []

    # Go through each repo
    # Search for issues labeled "help wanted" or "good first issue"

    for r in repos_with_topic:

        # Set up API request
        org_name = r['org_name']
        repo_name = r['repo_name']
        url = f"{GH_SEARCH_BASE_URL}/issues"
        query = f"repo:{org_name}/{repo_name} label:{issue_labels} state:open is:issue"

        params = {
                "q": query
                }

        help_wanted_issues_req = get_json(url, headers, params)

        if 'items' in help_wanted_issues_req:
            help_wanted_issues = help_wanted_issues_req['items']
        else:
            print("Key 'items' not found.")
            return help_wanted_issues_req

        for i in help_wanted_issues:

            # Create copy of the repo dict
            hw_issue = r.copy()

            # Create csv string of label names
            labels = [x['name'] for x in i['labels']]
            labels = ", ".join(labels)

            # Convert dates to human readable format
            created_at = datetime.strptime(i['created_at'], "%Y-%m-%dT%H:%M:%SZ").strftime("%d %B %Y")
            updated_at = datetime.strptime(i['updated_at'], "%Y-%m-%dT%H:%M:%SZ").strftime("%d %B %Y")

            # Add fields for this issue to the dict
            hw_issue['issue_url'] = i['html_url']
            hw_issue['issue_title'] = i['title']
            hw_issue['created_at'] = created_at
            hw_issue['updated_at'] = updated_at
            hw_issue['labels'] = labels

            # Add this dict to list of all help wanted issues
            all_help_wanted_issues.append(hw_issue)

    count_issues = len(all_help_wanted_issues)
    print(f"Found {count_issues} issues.\n")
    return all_help_wanted_issues


# Initialize empty list to hold all issues
all_issues = []

# Loop through all orgs, get repos and issues
# Add issues to all_issues list

# Note rate limit is 30 requests per minute for search
# https://docs.github.com/en/rest/search/search?apiVersion=2022-11-28
# Script will need modification if any LPs exceed 30 repos to query.
# DC is currently at 22.

for i in ALL_ORGS:
    try:
        repos = get_repos_by_topic(i, topics)
        issues = get_help_wanted_issues(repos, labels)
        all_issues.extend(issues)
    except Exception as e:
        print(f"Error with repo: '{i}', '{e}'")
        continue
    print("Pausing 60 seconds to reset GH API rate limit...\n")
    time.sleep(60)

filename = '_data/lessons_help_wanted.json'
print(f'Total {len(all_issues)} issues retrieved')
print(f'Saving to file {filename}')

try:
    with open(filename, 'w') as file:
        json.dump(all_issues, file)
except Exception as e:
    print(f'An error occured when writing to {filename}: {e}')
