# Refactored for stuff...
# p4debugscan changed to use errno module as well
from __future__ import print_function
import errno # for error handling
import os
import re
import subprocess
import sys


def print_usage():
    """Print usage information and exit."""
    print('p4sizes.py shows the size of the last N revisions of a file in Perforce')
    print('usage: p4sizes.py filename N')
    print('ex   : p4sizes.py //valvegames/rel/hl2/game/bin/engine.dll 10')
    print('       (shows the sizes of the last 10 checkins to engine.dll)')
    sys.exit(1)


def get_changelist_numbers(filename, n_revisions):
    cmd = ['p4', 'changes', '-m', str(n_revisions), filename]
    try:
        output = subprocess.check_output(
            cmd, stderr=subprocess.STDOUT, universal_newlines=True
        )
    except subprocess.CalledProcessError as e:
        print("Error running 'p4 changes': {}".format(e.output.strip()),
              file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        if e.errno == errno.ENOENT:
            print("Error: 'p4' command not found.", file=sys.stderr)
        else:
            print("Error: {}".format(e), file=sys.stderr)
        sys.exit(1)

    changelist_numbers = []
    changelist_re = re.compile(
        r'change (?P<num>\d+?) on (?P<date>.+?) ', re.IGNORECASE
    )
    remaining = output

    while True:
        match = changelist_re.search(remaining)
        if not match:
            break
        remaining = remaining[match.end():]
        changelist_numbers.append([match.group('num'), match.group('date')])

    return changelist_numbers


def get_file_size(filename, change_num):
    cmd = ['p4', 'sizes', '{}@{}'.format(filename, change_num)]
    try:
        return subprocess.check_output(
            cmd, stderr=subprocess.STDOUT, universal_newlines=True
        )
    except subprocess.CalledProcessError as e:
        print("Error running 'p4 sizes' for changelist {}: {}".format(
            change_num, e.output.strip()), file=sys.stderr)
        return None


def main():
    if len(sys.argv) < 3:
        print_usage()

    filename = sys.argv[1]
    n_revisions = sys.argv[2]

    changelist_numbers = get_changelist_numbers(filename, n_revisions)

    for change_num, change_date in changelist_numbers:
        size_output = get_file_size(filename, change_num)
        if size_output is not None:
            print('{}: {}'.format(change_date, size_output.rstrip()))


if __name__ == '__main__':
    main()
