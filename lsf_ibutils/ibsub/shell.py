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
    # If any of this errors at any point just return None.
    current_proc = Process(os.getpid())
    if current_proc is None:
        return None

    parent_proc = current_proc.parent
    if parent_proc is None:
        return None

    shell_path = parent_proc.exe
    for shell in SHELLS:
        shell_basename = os.path.basename(shell_path)
        # Some shells can be called by name and version e.g. `bash-4.1'. This
        # code handles that kind of call.
        if shell in shell_basename:
            return shell

    return None


if __name__ == '__main__':
    print(detect())
