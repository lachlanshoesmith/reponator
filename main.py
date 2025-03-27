#!/usr/bin/python
import csv
import sys
import os
import requests as re

GITHUB_TOKEN = ""
GITHUB_ORGANISATION = ""
REPOSITORY_PREFIX = ""

ORGANISATION_REPOS = f"https://api.github.com/orgs/{GITHUB_ORGANISATION}/repos"
HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "X-GitHub-Api-Version": "2022-11-28"
}

repo_options_base = {
    "description": "25T1 Training Program project",
    "homepage": "",
    "private": False,
    "has_issues": True,
    "has_projects": True,
    "has_wiki": True
}


def usage():
    return f'Usage: {os.path.basename(__file__)} <filename>'


try:
    filename = sys.argv[1]
except IndexError:
    sys.exit(usage())

data = {}

try:
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headings = next(reader)
        for row in list(reader):
            # check if data already has key headings[0]
            if data.get(row[0]) is None:
                try:
                    data[row[0]] = {
                        headings[1]: row[1].split('|'),
                        headings[2]: row[2].split('|')
                    }
                    if 'TODO' in data[row[0]][headings[1]] or 'TODO' in data[row[0]][headings[2]]:
                        print(f'⚠️ Warning: TODO(s) found in {row[0]}.')
                except IndexError:
                    sys.exit('The following row is incomplete: ' + str(row))
            else:
                sys.exit(
                    f'"{filename}" contains more than one entry for "{headings[0]}"')

except FileNotFoundError:
    sys.exit(
        f'"{filename}" does not exist.\n' + usage())

to_continue = input('Ready to create repositories. Continue (y)? ')
if to_continue.lower() != 'y':
    sys.exit()

for team, members in data.items():
    repo_name = REPOSITORY_PREFIX + team.lower()
    repo_options = repo_options_base
    repo_options.name = repo_name

    res = re.post(ORGANISATION_REPOS, headers=HEADERS,
                  json=repo_options, timeout=10)

    if res.status_code == 201:
        print('🌟 Created' + repo_name)
    else:
        print('🛑 Failed to create' + repo_name)
        print(res.json())
