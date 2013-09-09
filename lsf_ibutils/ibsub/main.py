#!/usr/bin/env python
""":mod:`lsf_ibutils.main` -- Program entry point
"""

from __future__ import print_function
import argparse
import sys

import pinject

from lsf_ibutils import ibsub
from lsf_ibutils import metadata
from lsf_ibutils.ibsub.binding_specs import IbsubBindingSpec
from lsf_ibutils.ibsub import output
from lsf_ibutils.ibsub import shell


def main(argv):
    """Program entry point.

    :param argv: command-line arguments
    :type argv: :class:`list`
    """
    obj_graph = pinject.new_object_graph(binding_specs=[IbsubBindingSpec()])
    # TODO Not the cleanest solution.
    ibsub.obj_graph = obj_graph
    return obj_graph.provide(Main)(argv)


class Main(object):
    @pinject.copy_args_to_internal_fields
    def __init__(self, exec_prompts, prompt_command,
                 build_script, build_command):
        pass

    def __call__(self, argv):
        author_strings = []
        for name, email in zip(metadata.authors, metadata.emails):
            author_strings.append('Author: {0} <{1}>'.format(name, email))

        epilog = '''
{project} {version}

{authors}
URL: <{url}>
'''.format(
            project=metadata.project,
            version=metadata.version,
            authors='\n'.join(author_strings),
            url=metadata.url)

        arg_parser = argparse.ArgumentParser(
            prog=argv[0],
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=metadata.description,
            epilog=epilog)
        arg_parser.add_argument(
            '-v', '--version',
            action='version',
            version='{0} {1}'.format(metadata.project, metadata.version))
        type_choices = ['script', 'command']
        arg_parser.add_argument(
            '-t', '--type',
            choices=type_choices,
            default=type_choices[0],
            help='type of output')
        # XXX TODO Test this code
        default_syntax = shell.detect()
        if default_syntax is None:
            default_syntax = 'bash'
        arg_parser.add_argument(
            '-s', '--syntax',
            choices=output.SYNTAXES,
            default=default_syntax,
            help='shell syntax to use in conjuction with --type script')

        args = arg_parser.parse_args(args=argv[1:])
        flags = self._exec_prompts()
        command = self._prompt_command()

        if args.type == 'script':
            out = self._build_script(flags, command, args.syntax)
        else:
            out = self._build_command(flags, command)

        print(out)

        return 0


def entry_point():
    """Zero-argument entry point for use with setuptools/distribute."""
    raise SystemExit(main(sys.argv))


if __name__ == '__main__':
    entry_point()
