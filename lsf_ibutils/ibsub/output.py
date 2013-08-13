""":mod:`lsf_ibutils.ibsub.output` -- Command and script output formatting
"""
# This function has an interesting history of being undocumented, deprecated,
# etc. However, it seems to be portable across Python 2 and 3. See here:
# <http://docs.python.org/2/library/pipes.html#pipes.quote>
from pipes import quote
import shlex

import pinject


SYNTAXES = [
    'bash',
    'zsh',
    'tcsh',
    'ksh',
    'python',
]
"""Supported shell output syntaxes."""


def build_command(flags, command):
    """Build a bsub command string from a list of flags.

    :param flags: a list of flags
    :type flags: :class:`list` of :class:`tuple`
    :param command: command to run, in shell syntax \
    e.g., ``"mpirun.lsf './my executable' --flag"``
    :type command: :class:`str`
    :return: the command string
    :rtype: :class:`str`
    """
    quoted_args = ['bsub']
    for flag_tuple in flags:
        for flag in flag_tuple:
            quoted_args.append(quote(flag))
    # Command is assumed to already be in shell syntax, so it gets passed
    # through unquoted.
    quoted_args.append(command)
    return ' '.join(quoted_args)


class BuildScript(object):
    @pinject.copy_args_to_internal_fields
    def __init__(self, today_datetime):
        pass

    def __call__(self, flags, command, syntax):
        """Build a script string from a list of flags and given syntax. The
        command is assumed to already be in shell syntax, so it is passed
        through unquoted. If using Python syntax, shell metacharacters will not
        be recognized.

        :param flags: a list of flags
        :type flags: :class:`list` of :class:`tuple`
        :param syntax: shell syntax to use
        :type syntax: :class:`str`, one of :data:`SHELLS`
        :param command: command to run, in shell syntax \
        e.g., ``"mpirun.lsf './my executable' --flag"``
        :type command: :class:`str`
        :return: the script as a string
        :rtype: class:`str`
        """
        if syntax not in SYNTAXES:
            raise ValueError(
                'invalid shell syntax {0}, valid syntaxes are {1}'.format(
                    repr(syntax),
                    ', '.join([repr(s) for s in SYNTAXES])))
        formatted_time = self._today_datetime.strftime('%Y-%m-%d %H:%M:%S')
        lines = [
            '#!/usr/bin/env {0}'.format(syntax),
            '#',
            '# LSF batch script',
            '# Generated by ibsub on {0}'.format(formatted_time),
        ]

        if syntax == 'python':
            lines.append('# Compatible with Python >= 2.4')

        lines.append('#')
        for flag_tuple in flags:
            lines.append('#BSUB {0}'.format(
                ' '.join([quote(flag) for flag in flag_tuple])))
        lines.append('')

        if syntax == 'python':
            command_list_string = repr(shlex.split(command))
            lines += [
                'import subprocess',
                "subprocess.call({0})".format(command_list_string),
            ]
        else:
            # Command is assumed to already be in shell syntax, so it gets
            # passed through unquoted.
            lines.append(command)

        return '\n'.join(lines) + '\n'
