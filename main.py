#!/usr/bin/python
import csv
import sys
import os
import subprocess


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
