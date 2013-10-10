#!/usr/bin/env python
# This file is executable mostly for testing.
""":mod:`lsf_ibutils.ibsub.shell` -- Shell detection
"""

from __future__ import print_function
import os

from psutil import Process


SHELLS = [
    'bash',
    'zsh',
    'tcsh',
    'ksh',
]
"""Shells detected by this module."""


def detect():
    """Detect the currently running shell.

    Shells tested are listed in :data:`SUPPORTED_SHELLS`

    If the shell cannot be detected, ``None`` is returned.

    :return: the short name of the shell if possible to detect, else ``None``
    :rtype: :class:`str`
    """
    # The pytest-cov plugin (`paver coverage') reports this function as not
    # covered. Ignore it, because this function is covered by launching a
    # subprocess and there is no way the coverage plugin would be able to
    # detect that.

    # Keep going up the hierarchy to try to detect a shell. When running from
    # source code, this should be the next process up. Frozen PyInstaller
    # bundles will insert one extra process in there. This also supports
    # auto-detection of the shell from scripts. If any of this errors at any
    # point just return None.
    proc = Process(os.getpid())
    if proc is None:
        return None

    while True:
        proc = proc.parent
        if proc is None:
            break

        proc_basename = os.path.basename(proc.exe)
        for shell in SHELLS:
            # Some shells can be called by name and version
            # e.g. `bash-4.1'. This code handles that kind of call.
            if shell in proc_basename:
                return shell

    return None


if __name__ == '__main__':
    print(detect())
