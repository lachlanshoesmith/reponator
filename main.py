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
    return f'Usage: {os.path.basename(__file__)} <filename> <github_token> <github_organisation> [repository_prefix] [repository_suffix] [list,of,universal,admins]'


def add_collaborator(collaborator, permission):
    collab_url = f"https://api.github.com/repos/{github_organisation}/{repo_name}/collaborators/{collaborator}"
    collab_res = re.put(collab_url, headers=headers, json={
        "permission": permission}, timeout=10)
    if collab_res.status_code in [201, 204]:
        print(f'✅ Added {collaborator} with {permission} access')


try:
    filename = sys.argv[1]
    github_token = sys.argv[2]
    github_organisation = sys.argv[3]
    repository_prefix = sys.argv[4] if len(sys.argv) >= 5 else ''
    repository_suffix = sys.argv[5] if len(sys.argv) >= 6 else ''
    universal_admins = sys.argv[6].split(',') if len(sys.argv) >= 7 else []

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
        print(f'🏃‍➡️ Skipping {team}...\n')
        continue

    repo_name = repository_prefix + team.lower() + repository_suffix
    repo_options = REPO_OPTIONS_BASE
    repo_options['name'] = repo_name

    res = re.post(organisation_repos, headers=headers,
                  json=repo_options, timeout=10)

    if res.status_code == 201:
        print('🌟 Created ' + repo_name)
    else:
        print('🛑 Failed to create ' + repo_name)
        print(res.json())

    for admin in universal_admins:
        add_collaborator(admin, "admin")

    for lead in members['Leads']:
        add_collaborator(lead, "admin")

    for trainee in members['Trainees']:
        add_collaborator(trainee, "push")

    print()
