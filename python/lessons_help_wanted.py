#!/usr/bin/env python3

# Import all the things
import json
import os
import requests

# Authenticate
GH_TOKEN = os.environ['GITHUB_PAT']

HEADERS = {
    "Authorization": f"token {GH_TOKEN}",
    "Accept": "application/vnd.github+json"
}

ORGS = ["swcarpentry", "datacarpentry", "librarycarpentry", "carpentries", "hpc-carpentry", "aicarpentry"]
ORG_TOPICS = ['stable', 'helpwanted-list']
ISSUE_LABELS = ["good first issue", "help wanted"]


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


def get_org_info(org):
    """
    Takes org name as a string and returns
    a dict with the org name and url
    """

    url = f"https://api.github.com/orgs/{org}"
    org_info = get_json(url, HEADERS)
    org_dict = {'org_url': org_info['html_url'], 'org_full_name': org_info['name']}
    return org_dict


def get_repos_as_dict(org, topics):
    """
    Get all repositories in a GitHub org that have all of the specified topics.
    Takes two parameters:
    org: GH organization name
    topics: list of topics as strings
    Returns dict with repo name, description, and url
    """

    print(f"\n**Retrieving all repos from {org} organization with topics: {topics}**\n")
    repos = []
    page = 1
    query = f"org:{org} archived:false topic:" + ",".join([f"{topic}" for topic in topics])

    while True:
        params = {
            "q": query,
            "per_page": 100,
            "page": page
        }
        search_url = "https://api.github.com/search/repositories"
        data = get_json(search_url, HEADERS, params=params)

        if not data or not data.get("items"):
            break

        for repo in data["items"]:
            repo_dict = {
                'repo_name': repo['name'],
                'repo_description': repo['description'],
                'repo_url': repo['html_url']
            }
            print(f" - {repo_dict['repo_name']}, {repo_dict['repo_url']}")
            repos.append(repo_dict)

        if len(data["items"]) < 100:
            break

        page += 1

    print(f"    {len(repos)} repos returned\n")

    return repos


def get_issues_from_repo_dict(org, repo_dicts, labels):
    """
    Function takes three params:
    org name (str)
    repo dicts (list, as created in previous function)
    labels(list)
    Returns dict of issues with labels from that org, filtered to provided repos,
    including repo/org info
    """

    all_issues = []
    issue_keys = ['html_url', 'title', 'created_at', 'updated_at', 'labels']
    repo_lookup = {repo['repo_name']: repo for repo in repo_dicts}

    # Get org info; this will be used later when building the dict
    org_info_dict = get_org_info(org)

    print(f"Fetching issues from {org}...")
    page = 1
    label_query = ",".join([f'"{label}"' for label in labels])
    query = f"org:{org} is:issue is:open label:{label_query}"

    while True:
        params = {'q': query, 'per_page': 100, 'page': page}
        issues_url = "https://api.github.com/search/issues"
        print(issues_url, params)
        issues = get_json(issues_url, HEADERS, params)

        if not issues or not issues.get('items'):
            break

        # Add fetched issues, keeping only repositories in our topic-filtered set.
        for issue in issues['items']:
            repo_name = issue['repository_url'].rsplit('/', 1)[-1]
            if repo_name not in repo_lookup:
                continue

            repo_dict = repo_lookup[repo_name]
            issue_dict = {key: issue[key] for key in issue_keys}
            labels_by_name = [x['name'] for x in issue_dict['labels']]
            issue_dict['labels'] = labels_by_name
            issue_dict['issue_title'] = issue_dict.pop('title')
            issue_dict['issue_url'] = issue_dict.pop('html_url')

            issue_dict['org'] = org
            issue_dict['org_url'] = org_info_dict['org_url']
            issue_dict['org_full_name'] = org_info_dict['org_full_name']

            issue_dict['repo_url'] = repo_dict['repo_url']
            issue_dict['repo_description'] = repo_dict['repo_description']
            all_issues.append(issue_dict)

        if len(issues['items']) < 100:
            break
        page += 1

    print(f" - {len(all_issues)} issues returned")
    return all_issues


def convert_data_types(issue_dict):
    """
    Takes dict of issues that includes at least the following keys:
    ['created_at',
     'updated_at',
     'labels',]
    Converts the 'labels' list and the 'created_at' and 'updated_at' dates to human readable strings
    """

    if isinstance(issue_dict, dict):
        try:
            issue_dict['created_at'] = issue_dict['created_at'][:10]
            issue_dict['updated_at'] = issue_dict['updated_at'][:10]

            list_string = ", ".join(issue_dict['labels'])
            issue_dict['labels'] = list_string
            return issue_dict

        except KeyError as e:
            print(f"Key not found: {e}")
            return

    else:
        print(f"Not a dict: {issue_dict}")
        return

def make_help_wanted_feed(path):
    full_issue_list = []

    for org in ORGS:
        org_repos = get_repos_as_dict(org, ORG_TOPICS)
        org_issues = get_issues_from_repo_dict(org, org_repos, ISSUE_LABELS)
        full_issue_list.extend(org_issues)

    # Format date and list data types
    formatted_full_issue_list = []
    for issue in full_issue_list:
        formatted_issue = convert_data_types(issue)
        formatted_full_issue_list.append(formatted_issue)

    # Sort issues by created date (most recent first)
    formatted_full_issue_list.sort(key=lambda x: x['created_at'], reverse=True)

    print(len(formatted_full_issue_list), 'issues retrieved')

    # Save output to json file

    print(f'Saving to file {path}')

    try:
        with open(path, 'w') as file:
            json.dump(formatted_full_issue_list, file)
    except Exception as e:
        print(f'An error occured when writing to {path}: {e}')


if __name__ == "__main__":
    make_help_wanted_feed('_data/lessons_help_wanted.json')
