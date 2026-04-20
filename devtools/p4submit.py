#!/usr/bin/env python
# Okay, this has to stop, I'm tired boss...
from __future__ import print_function

import getopt
import os
import re
import sys
import subprocess

def usage():
    print('checks in all open files in the default changelist, aggregating change comments from the provided list', file=sys.stderr)
    print('', file=sys.stderr)
    print('usage:', file=sys.stderr)
    print(sys.argv[0] + ' [-c p4client] [-p p4port] [-u p4user] [-d changelog (prefix)] [--changes "list of change numbers"]', file=sys.stderr)
    print('', file=sys.stderr)
    print('the list of changes must either be the last argument, or be quoted, so ', file=sys.stderr)
    print(sys.argv[0] + ' ... --changes 1 2 3  [ok] ', file=sys.stderr)
    print(sys.argv[0] + ' ... --changes "1 2 3" ... [ok]', file=sys.stderr)
    print(sys.argv[0] + ' ... -changes 1 2 3 ... [bad]', file=sys.stderr)

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "c:p:u:d:", ["changes="])
    except getopt.GetoptError as err:
        print(str(err), file=sys.stderr)
        usage()
        sys.exit(-1)

    p4user = None
    p4client = None
    p4port = None
    changelog = None
    changes = []
    p4cmdbase = ["p4"]
    for opt, arg in opts:
        if opt == "-c":
            p4cmdbase.extend([opt, arg])
            p4client = arg
        elif opt == "-p":
            p4cmdbase.extend([opt, arg])
            p4port = arg
        elif opt == "-u":
            p4cmdbase.extend([opt, arg])
            p4user = arg
        elif opt == "-d":
            changelog = arg
        elif opt == "--changes":
            changes = arg.split()
            if args:
                changes.extend(args)

    if p4user is None:
        p4user = os.getenv("P4USER")
    if p4client is None:
        p4client = os.getenv("P4CLIENT")
    if p4port is None:
        p4port = os.getenv("P4PORT")

    if p4user is None or p4client is None or p4port is None:
        print("one or more p4 environment variables (p4user, p4client, p4port) aren't set.", file=sys.stderr)
        usage()
        sys.exit(-1)

    # Get the list of opened files.
    try:
        output = subprocess.check_output(
            p4cmdbase + ["opened", "-c", "default"],
            universal_newlines=True,
            stderr=subprocess.PIPE
        )
    except subprocess.CalledProcessError as e:
        print("Error running 'p4 opened': {}".format(e.stderr.strip()), file=sys.stderr)
        sys.exit(e.returncode)
    except FileNotFoundError:
        print("Error: 'p4' command not found.", file=sys.stderr)
        sys.exit(1)

    open_files = []
    filere = re.compile(r"(.*)#.*\n")
    for line in output.splitlines(True):
        m = filere.match(line)
        if m is not None:
            open_files.append(m.groups()[0])

    if not open_files:
        sys.stderr.write("no files to submit from the default changelist\n")
        sys.exit(0)

    # Get the change notes from the specified changes.
    change_lines = []
    for change in changes:
        try:
            desc_output = subprocess.check_output(
                p4cmdbase + ["describe", "-s", change],
                universal_newlines=True,
                stderr=subprocess.PIPE
            )
        except subprocess.CalledProcessError as e:
            print("Error running 'p4 describe -s {}': {}".format(change, e.stderr.strip()), file=sys.stderr)
            sys.exit(e.returncode)

        stopre = re.compile(r"Affected files \.\.\.")
        for line in desc_output.splitlines():
            if stopre.match(line):
                break
            change_lines.append(line.strip())

    change_spec = ''
    change_spec += 'Change: new\n'
    change_spec += 'Client: {}\n'.format(p4client)
    change_spec += 'User: {}\n'.format(p4user)
    change_spec += 'Description:\n'

    if changelog is not None:
        change_spec += '\t{}\n\n'.format(changelog)
    if change_lines:
        change_spec += '\t{}\n\n'.format("Changes included in this submit:")
    for line in change_lines:
        change_spec += '\t{}\n'.format(line)

    change_spec += 'Files:\n'
    for fname in open_files:
        change_spec += '\t{}\n'.format(fname)

    try:
        proc = subprocess.Popen(
            p4cmdbase + ["submit", "-i"],
            stdin=subprocess.PIPE,
            stdout=sys.stdout,
            stderr=sys.stderr,
            universal_newlines=True
        )
        proc.communicate(change_spec)
        sys.exit(proc.returncode)
    except Exception as e:
        print("Error submitting changelist: {}".format(e), file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
