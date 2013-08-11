import os
import sys
import inspect
import subprocess

import pytest
parametrize = pytest.mark.parametrize

from lsf_ibutils.ibsub import shell

## Python 2.6 subprocess.check_output compatibility.
if 'check_output' not in dir(subprocess):
    def check_output(cmd_args, *args, **kwargs):
        proc = subprocess.Popen(
            cmd_args, *args,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)
        out, err = proc.communicate()
        if proc.returncode != 0:
            raise subprocess.CalledProcessError(args)
        return out
    subprocess.check_output = check_output


class TestDetect(object):
    # Don't include python because it needs a special setup.
    @parametrize('shell_exe', shell.SHELLS)
    def test_detects_supported_shell(self, shell_exe):
        try:
            # Don't use subprocess.check_call because ksh exits with 2 when
            # running a version check (come on...).
            #
            # This also has the happy side effect of printing the shell version
            # upon test failure.
            subprocess.call([shell_exe, '--version'])
        except OSError:
            # This is a probably a `No such file or directory' error. That
            # probably means the system could not find the executable. No
            # matter whether any of this is true, we most likely cannot run the
            # shell. Skip it.
            pytest.skip("cannot run `{0}' shell".format(shell_exe))

        # Start an interactive shell session. Weird things having to do with
        # the parent process can result when using the -c flag, and that's not
        # what we're testing anyway.
        shell_proc = subprocess.Popen(
            [shell_exe],
            # Pass the PYTHONPATH and PATH variables to the new shell.
            env={
                'PYTHONPATH': ':'.join(sys.path),
                'PATH': os.getenv('PATH', ''),
            },
            # Allow passing to stdin and reading from stdout. Don't care about
            # stderr.
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE)
        # Use the python currently running.
        shell_command = sys.executable + ' ' + inspect.getsourcefile(shell)
        # communicate() will wait for the process to terminate.
        out, err = shell_proc.communicate(
            (shell_command + '\n').encode('ascii'))

        # Will be printed with a newline (could remove this, since we control
        # the executable, I guess).
        detected_shell = out.rstrip()
        assert detected_shell == shell_exe.encode('ascii')
