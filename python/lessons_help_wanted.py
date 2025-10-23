#!/usr/bin/env python

# Import all the things
import requests
import os
import json

# Authenticate
GH_TOKEN = os.environ['GITHUB_PAT']

headers = {
    "Authorization": f"token {GH_TOKEN}",
    "Accept": "application/vnd.github+json"
}


# Identify all Carpentries organizations
ORGS = ["swcarpentry", "datacarpentry", "librarycarpentry", "carpentries"]
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
    org_info = get_json(url, headers)
    # r = requests.get(url, headers=headers)
    # data = org_info.json()
    # print(data['name'], data['description'], data['html_url'])
    org_dict = {'org_url': org_info['html_url'], 'org_full_name': org_info['name']}
    return org_dict


def get_repos_as_dict(org, topics):
    """
    Get all repositories in a GitHub org that have any of the specified topics.
    Takes two parameters:
    org: GH organization name
    topics: list of topics as strings
    Returns dict with repo name, description, and url
    """

    print(f"\n**Retrieving all repos from {org} organization with topics: {topics}**\n")
    repos = []
    page = 1

    while True:
        url = f"https://api.github.com/orgs/{org}/repos?per_page=100&page={page}"
        data = get_json(url, headers)

        if not data:
            break

        for repo in data:
            if repo.get("archived"):
                # Skip archived repos
                continue

            repo_name = repo["name"]

            topics_url = f"https://api.github.com/repos/{org}/{repo_name}/topics"
            topics_response = get_json(topics_url, headers)

            repo_topics = topics_response.get("names", [])

            repo_dict = {}
            if any(topic in repo_topics for topic in topics):
                repo_url = repo['html_url']
                repo_description = repo['description']
                print(f" - {repo_name}, {repo_url}")
                repo_dict['repo_name'] = repo_name
                repo_dict['repo_description'] = repo_description
                repo_dict['repo_url'] = repo_url

                repos.append(repo_dict)

        page += 1

    print(f"    {len(repos)} repos returned\n")

    return repos


def get_issues_from_repo_dict(org, repo_dict, labels):
    """
    Function takes three params:
    org name (str)
    repo dict (as created in previous function)
    labels(list)
    Returns dict of issues with labels from that repo/org, including repo/org info
    """

    all_issues = []
    issue_keys = ['html_url', 'title', 'created_at', 'updated_at', 'labels']

    # Get org info; this will be used later when building the dict
    org_info_dict = get_org_info(org)

    repo_name = repo_dict['repo_name']
    print(f"Fetching issues from {org}/{repo_name}...")
    for label in labels:
        params = {'labels': label, 'state': 'open'}
        issues_url = f"https://api.github.com/repos/{org}/{repo_name}/issues"
        issues = get_json(issues_url, headers, params)

        if not issues:
            continue

        # Add the fetched issues to our dictionary.
        for issue in issues:
            issue_dict = {key: issue[key] for key in issue_keys}
            labels_by_name = [x["name"] for x in issue_dict['labels']]
            issue_dict['labels'] = labels_by_name
            issue_dict['issue_title'] = issue_dict.pop('title')
            issue_dict['issue_url'] = issue_dict.pop('html_url')

            issue_dict['org'] = org
            issue_dict['org_url'] = org_info_dict['org_url']
            issue_dict['org_full_name'] = org_info_dict['org_full_name']

            issue_dict['repo_url'] = repo_dict['repo_url']
            issue_dict['repo_description'] = repo_dict['repo_description']
            all_issues.append(issue_dict)

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


full_issue_list = []

for org in ORGS:
    org_repos = get_repos_as_dict(org, ORG_TOPICS)
    for repo in org_repos:
        org_issues = get_issues_from_repo_dict(org, repo, ISSUE_LABELS)
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

filename = '_data/lessons_help_wanted.json'
print(f'Saving to file {filename}')

try:
    with open(filename, 'w') as file:
        json.dump(formatted_full_issue_list, file)
except Exception as e:
    print(f'An error occured when writing to {filename}: {e}')