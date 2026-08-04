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
LIFE_CYCLE_TAGS = ["pre-alpha", "alpha", "beta", "stable", "on-hold", "template"]
HUMAN_LANGUAGE = ["english", "spanish"]


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


def get_lesson_repos_for_org(org, ignore_archived=True):
    """
    Retrieve repositories for one org using a single paginated search query.
    Results are pre-filtered to repos that contain the lesson topic.
    """
    print(f"\nRetrieving lesson repositories from {org}...")
    repos = []
    page = 1

    query_parts = [f"org:{org}", "topic:lesson"]
    if ignore_archived:
        query_parts.append("archived:false")
    query = " ".join(query_parts)

    while True:
        params = {"q": query, "per_page": 100, "page": page}
        data = get_json("https://api.github.com/search/repositories", HEADERS, params)
        items = data.get("items", [])

        if not items:
            break

        for repo in items:
            if repo.get("private", False):
                continue

            repos.append(
                {
                    "carpentries_org": org,
                    "repo": repo["name"],
                    "repo_url": repo["html_url"],
                    "full_name": repo["full_name"],
                    "description": repo.get("description") or "",
                    "rendered_site": repo.get("homepage") or "",
                    "github_topics": repo.get("topics", []),
                }
            )

        if len(items) < 100:
            break
        page += 1

    print(f"  {len(repos)} lesson repositories returned")
    return repos


def extract_single_tag(repo_data, dict_tags, field_name):
    """
    Extract exactly one matching tag and remove dictionary tags from github_topics.
    """
    matched_tags = [tag for tag in repo_data["github_topics"] if tag in dict_tags]

    if len(matched_tags) > 1:
        raise ValueError(f"More than one tag detected for: {repo_data['full_name']}")

    if len(matched_tags) == 0:
        tags_str = ", ".join(dict_tags)
        raise ValueError(f"No tag found among ({tags_str}) for repo: {repo_data['full_name']}")

    repo_data[field_name] = matched_tags[0]
    repo_data["github_topics"] = [
        topic for topic in repo_data["github_topics"] if topic not in dict_tags
    ]

    return repo_data


def make_lessons_feed(path):
    all_repos = []
    for org in ORGS:
        all_repos.extend(get_lesson_repos_for_org(org, ignore_archived=True))

    extracted = []
    for repo in all_repos:
        repo = extract_single_tag(repo, LIFE_CYCLE_TAGS, "life_cycle")
        repo = extract_single_tag(repo, HUMAN_LANGUAGE, "human_language")

        extracted.append(
            {
                "carpentries_org": repo["carpentries_org"],
                "repo": repo["repo"],
                "repo_url": repo["repo_url"],
                "description": repo["description"],
                "rendered_site": repo["rendered_site"],
                "life_cycle": repo["life_cycle"],
                "human_language": repo["human_language"],
                "github_topics": repo["github_topics"],
            }
        )

    print(f'Saving to file {path}')

    try:
        with open(path, 'w') as file:
            json.dump(extracted, file)
    except Exception as e:
        print(f'An error occured when writing to {path}: {e}')


if __name__ == "__main__":
    make_lessons_feed("_data/lessons.json")
