#!/usr/bin/python
import csv
import sys
import os
import requests as re

REPO_OPTIONS_BASE = {
    "description": "25T1 Training Program project",
    "homepage": "",
    "private": False,
    "has_issues": True,
    "has_projects": True,
    "has_wiki": True
}


def usage():
    return f'Usage: {os.path.basename(__file__)} <filename> <github_token> <github_organisation> [repository_prefix] [repository_suffix]'


try:
    filename = sys.argv[1]
    github_token = sys.argv[2]
    github_organisation = sys.argv[3]
    if len(sys.argv) >= 5:
        REPOSITORY_PREFIX = sys.argv[4]
        if len(sys.argv) == 6:
            REPOSITORY_SUFFIX = sys.argv[5]
        else:
            REPOSITORY_SUFFIX = ''
    else:
        REPOSITORY_PREFIX = ''
        REPOSITORY_SUFFIX = ''

except IndexError:
    sys.exit(usage())

data = {}
organisation_repos = f"https://api.github.com/orgs/{github_organisation}/repos"
headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {github_token}",
    "X-GitHub-Api-Version": "2022-11-28"
}

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
                        print(
                            f'⚠️ Warning: TODO(s) found in {row[0]}. Will skip.')
                        data[row[0]]['skip'] = True
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
    if 'skip' in members:
        print(f'🏃‍➡️ Skipping {team}...')
        continue

    repo_name = REPOSITORY_PREFIX + team.lower() + REPOSITORY_SUFFIX
    repo_options = REPO_OPTIONS_BASE
    repo_options['name'] = repo_name

    res = re.post(organisation_repos, headers=headers,
                  json=repo_options, timeout=10)

    if res.status_code == 201:
        print('🌟 Created ' + repo_name)
    else:
        print('🛑 Failed to create' + repo_name)
        print(res.json())

    for lead in members['Leads']:
        collab_url = f"https://api.github.com/repos/{github_organisation}/{repo_name}/collaborators/{lead}"
        res = re.put(collab_url, headers=headers,
                     json={"permission": "admin"}, timeout=10)

        if res.status_code in [201, 204]:
            print(f'✅ Added {lead} with admin access')

    for trainee in members['Trainees']:
        collab_url = f"https://api.github.com/repos/{github_organisation}/{repo_name}/collaborators/{trainee}"

        res = re.put(collab_url, headers=headers,
                     json={"permission": "push"}, timeout=10)

        if res.status_code in [201, 204]:
            print(f'✅ Added {trainee} with push access')
