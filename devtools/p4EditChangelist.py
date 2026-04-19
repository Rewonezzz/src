
from __future__ import print_function # for compatibility
import sys
import subprocess
import re

def print_usage():
    print("p4EditChangelist.py [changelist #]")
    print("    - Checks out all the files in the specified changelist.")

if len(sys.argv) < 2:
    print_usage()
    sys.exit(1)

changelist_number = sys.argv[1]

# Get the changelist description using 'p4 describe -s'.
# Added error handling, modernization.
try:
    proc = subprocess.Popen(
        ['p4', 'describe', '-s', changelist_number],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    stdout, stderr = proc.communicate()
    if proc.returncode != 0:
        print("Error running 'p4 describe': {}".format(stderr.strip()), file=sys.stderr)
        sys.exit(1)
except FileNotFoundError:
    print("Error: 'p4' command not found. Is Perforce installed and in PATH?", file=sys.stderr)
    sys.exit(1)

all_text = stdout

# Match each filename in the changelist description.
# Pattern: "... //depot/path/file.ext#revision "
filename_pattern = re.compile(r'\.\.\. (?P<fn>//.+)#\d+ ', re.IGNORECASE)
start_pos = 0

while True:
    match = filename_pattern.search(all_text, start_pos)
    if not match:
        break

    filename = match.group('fn')
    start_pos = match.end()

    # Edit the file in Perforce.
    print("Editing: {}".format(filename))
    try:
        subprocess.check_call(['p4', 'edit', filename])
    except subprocess.CalledProcessError as e:
        print("Error editing '{}': {}".format(filename, e), file=sys.stderr)
        # Continue with next file, or sys.exit(1) if you prefer to stop on first error.
