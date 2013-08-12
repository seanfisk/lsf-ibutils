from datetime import datetime

from pytest import fixture, raises

from lsf_ibutils.ibsub.output import build_command, BuildScript
from tests.helpers import assert_exc_info_msg


@fixture
def flags_simple():
    return [
        ('-J', 'awesomename'),
        ('-P', 'awesomeproj'),
        ('-n', '10'),
    ]


@fixture
def flags_ptile():
    return [('-R', 'span[ptile=10]')]


@fixture
def flags_spaces():
    return [
        ('-J', 'job name'),
        ('-P', 'proj name'),
        ('-q', 'queue with spaces'),
    ]


class TestBuildCommand(object):
    def test_simple(self, flags_simple):
        assert ('bsub -J awesomename -P awesomeproj -n 10 command arg1 arg2' ==
                build_command(flags_simple, 'command arg1 arg2'))

    def test_ptile(self, flags_ptile):
        assert ("bsub -R 'span[ptile=10]' command --flag flag_arg" ==
                build_command(flags_ptile, 'command --flag flag_arg'))

    def test_spaces(self, flags_spaces):
        assert ("bsub -J 'job name' -P 'proj name' "
                "-q 'queue with spaces' "
                "'command with spaces' 'arg with spaces'" ==
                build_command(
                    flags_spaces, "'command with spaces' 'arg with spaces'"))

    def test_special_chars(self):
        # Mostly just a test that pipes.quote is working properly.
        # The comnand special characters should pass right through.
        assert (
            "bsub -J 'job'\"'\"' nam[e]' -P 'pr{oj n}ame \escape' "
            "-q '`tick` $(param sub)' run {abc,def}" ==
            build_command([
                ('-J', "job' nam[e]"),
                ('-P', 'pr{oj n}ame \\escape'),
                ('-q', '`tick` $(param sub)'),
            ], 'run {abc,def}'))


class TestBuildScript(object):
    @fixture
    def build_script(self):
        return BuildScript(datetime(2013, 9, 12, 15, 24, 11))

    def test_invalid_shell(self, build_script):
        with raises(ValueError) as exc_info:
            build_script([], 'command', 'nosuchsh')
        assert_exc_info_msg(
            exc_info,
            "invalid shell syntax 'nosuchsh', valid syntaxes are "
            "'bash', 'zsh', 'tcsh', 'ksh', 'python'")

    def test_simple(self, build_script, flags_simple):
        assert '''#!/usr/bin/env bash
#
# LSF batch script
# Generated by ibsub on 2013-09-12 15:24:11
#
#BSUB -J awesomename
#BSUB -P awesomeproj
#BSUB -n 10

command arg1 arg2
''' == build_script(flags_simple, 'command arg1 arg2', 'bash')

    def test_ptile(self, build_script, flags_ptile):
        assert '''#!/usr/bin/env zsh
#
# LSF batch script
# Generated by ibsub on 2013-09-12 15:24:11
#
#BSUB -R 'span[ptile=10]'

command arg1 arg2
''' == build_script(flags_ptile, 'command arg1 arg2', 'zsh')

    def test_spaces(self, build_script, flags_spaces):
        assert '''#!/usr/bin/env tcsh
#
# LSF batch script
# Generated by ibsub on 2013-09-12 15:24:11
#
#BSUB -J 'job name'
#BSUB -P 'proj name'
#BSUB -q 'queue with spaces'

'command with spaces'
''' == build_script(flags_spaces, "'command with spaces'", 'tcsh')

    class TestPython(object):
        def test_simple(self, build_script, flags_simple):
            assert '''#!/usr/bin/env python
#
# LSF batch script
# Generated by ibsub on 2013-09-12 15:24:11
# Compatible with Python >= 2.4
#
#BSUB -J awesomename
#BSUB -P awesomeproj
#BSUB -n 10

import subprocess
subprocess.call(['command', '--flag', 'flag arg', 'arg1'])
''' == build_script(flags_simple, "command --flag 'flag arg' arg1", 'python')
