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

ORGS = ["carpentries-incubator", "carpentries-lab"]
LIFE_CYCLE_TAGS = ["pre-alpha", "alpha", "beta", "stable"]
COMMON_TAGS = ["carpentries", "carpentries-incubator", "carpentries-lesson", "carpentryconnect", "data-carpentry", "datacarpentry", "education", "lesson"]


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


def expand_full_name(org):
    names = {
        "carpentries": "The Carpentries",
        "carpentries-incubator": "The Carpentries Incubator",
        "carpentries-lab": "The Carpentries Lab",
        "datacarpentry": "Data Carpentry",
        "librarycarpentry": "Library Carpentry",
        "swcarpentry": "Software Carpentry",
    }
    if org not in names:
        raise ValueError(f"Unrecognised organisation: '{org}'")
    return names[org]


def get_org_repos_with_topics(org, ignore_archived=True):
    """
    Retrieve repositories for one org using a paginated search query.
    Topics are returned directly in the search payload.
    """
    print(f"\nRetrieving repositories from {org}...")
    repos = []
    page = 1

    query_parts = [f"org:{org}"]
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

    print(f"  {len(repos)} repositories returned")
    return repos


def has_lesson_topic(topics):
    return any("lesson" in topic for topic in topics)


def extract_tag(repo_data, dict_tags, field_name, approach="include", allow_multiple=False, allow_empty=False):
    if approach == "include":
        extracted_tag = [topic for topic in repo_data["github_topics"] if topic in dict_tags]
        remaining_topics = [
            topic for topic in repo_data["github_topics"] if topic not in dict_tags
        ]
    elif approach == "exclude":
        extracted_tag = [topic for topic in repo_data["github_topics"] if topic not in dict_tags]
        remaining_topics = [
            topic for topic in repo_data["github_topics"] if topic in dict_tags
        ]
    else:
        raise ValueError("Invalid value for approach. Use 'include' or 'exclude'.")

    if (not allow_multiple) and len(extracted_tag) > 1:
        raise ValueError(f"More than one tag detected for: {repo_data['full_name']}")

    if len(extracted_tag) == 0:
        if not allow_empty:
            tags_str = ", ".join(dict_tags)
            raise ValueError(
                f"No tag found among ({tags_str}) for repo: {repo_data['full_name']}"
            )
        repo_data[field_name] = [] if allow_multiple else ""
    else:
        repo_data[field_name] = extracted_tag if allow_multiple else [extracted_tag[0]]

    repo_data["github_topics"] = remaining_topics
    return repo_data


def check_missing_repo_info(rows, field):
    missing = [row["repo_url"] for row in rows if not str(row.get(field, "")).strip()]
    if missing:
        urls = "\n".join([f"  - {url}" for url in missing])
        return f"Missing repo {field} for:\n{urls}\n"
    return None


def check_repo_info(rows, fields):
    messages = [msg for msg in (check_missing_repo_info(rows, field) for field in fields) if msg]
    if not messages:
        print("No issues detected!")
        return

    github_env = os.getenv("GITHUB_ENV")
    if github_env:
        with open(github_env, "a") as env_file:
            env_file.write("EXIT_STATUS=1\n")

    for msg in messages:
        print(f"::warning::{msg}")


def make_community_lessons_feed(path):
    all_repos = []
    for org in ORGS:
        all_repos.extend(get_org_repos_with_topics(org, ignore_archived=True))

    lesson_repos = [repo for repo in all_repos if has_lesson_topic(repo["github_topics"])]

    processed = []
    for repo in lesson_repos:
        repo["org_full_name"] = expand_full_name(repo["carpentries_org"])
        repo = extract_tag(
            repo,
            LIFE_CYCLE_TAGS,
            "life_cycle_tag",
            approach="include",
            allow_multiple=False,
            allow_empty=False,
        )
        repo = extract_tag(
            repo,
            COMMON_TAGS,
            "lesson_tags",
            approach="exclude",
            allow_multiple=True,
            allow_empty=True,
        )
        processed.append(repo)

    check_repo_info(processed, ["description", "rendered_site"])

    print(f"Writing {len(processed)} records to {path}")
    with open(path, "w") as output_file:
        json.dump(processed, output_file)


if __name__ == "__main__":
    make_community_lessons_feed("_data/community_lessons.json")
