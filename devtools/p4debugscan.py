# IDK scans shit to do shit
# this one is likely broken imo, added errno fix
from __future__ import print_function

import errno
import os
import re
import stat
import subprocess
import sys
from ctypes import windll


def print_usage():
    print('p4debugscan.py scans for debug DLLs in the last N revisions of a file in Perforce')
    print('usage: p4debugscan.py filename N')
    print('alt  : p4debugscan.py filename -1   (will only look at filename on disk)')
    print('ex   : p4debugscan.py //valvegames/rel/hl2/game/bin/engine.dll 10')
    print('       (looks for debug versions in the past 10 revisions of engine.dll)')
    sys.exit(1)


def check_dll_debug(filename):
    # LoadLibraryW expects Unicode; in Python 2 we need to ensure filename is unicode
    if sys.version_info[0] == 2 and isinstance(filename, str):
        filename = filename.decode(sys.getfilesystemencoding())
    hdll = windll.kernel32.LoadLibraryW(filename)
    if not hdll:
        return False
    try:
        return windll.kernel32.GetProcAddress(hdll, b"BuiltDebug") != 0
    finally:
        windll.kernel32.FreeLibrary(hdll)


def get_changelist_numbers(filename, n_revisions):
    cmd = ['p4', 'changes', '-m', str(n_revisions), filename]
    try:
        output = subprocess.check_output(
            cmd, stderr=subprocess.STDOUT, universal_newlines=True
        )
    except subprocess.CalledProcessError as e:
        print("p4 error: {}".format(e.output), file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        if e.errno == errno.ENOENT:
            print("Error: 'p4' command not found.", file=sys.stderr)
        else:
            print("Error: {}".format(e), file=sys.stderr)
        sys.exit(1)

    changelist_numbers = []
    my_re = re.compile(r'change (?P<num>\d+?) on (?P<date>.+?) ', re.IGNORECASE)
    remaining = output

    while True:
        match = my_re.search(remaining)
        if not match:
            break
        remaining = remaining[match.end():]
        changelist_numbers.append([match.group('num'), match.group('date')])

    return changelist_numbers


def main():
    if len(sys.argv) < 3:
        print_usage()

    filename = sys.argv[1]
    n_revisions = sys.argv[2]

    if n_revisions == '-1':
        is_debug = check_dll_debug(filename)
        build_type = 'DEBUG' if is_debug else 'RELEASE'
        print('{}: {}'.format(filename, build_type))
    else:
        changelist_numbers = get_changelist_numbers(filename, n_revisions)
        test_dll_filename = 'p4debugscan_test.dll'

        try:
            for cl_num, date in changelist_numbers:
                subprocess.check_call(
                    ['p4', 'print', '-q', '-o', test_dll_filename,
                     '{}@{}'.format(filename, cl_num)]
                )

                is_debug = check_dll_debug(test_dll_filename)
                build_type = 'DEBUG' if is_debug else 'RELEASE'
                print('{}: {}@{} - {}'.format(date, filename, cl_num, build_type))
        finally:
            # Always clean up the temp file, even on error
            if os.path.exists(test_dll_filename):
                os.chmod(test_dll_filename, stat.S_IWRITE | stat.S_IREAD)
                os.unlink(test_dll_filename)


if __name__ == '__main__':
    main()
