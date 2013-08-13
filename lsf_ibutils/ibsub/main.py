#!/usr/bin/env python
""":mod:`lsf_ibutils.main` -- Program entry point
"""

from __future__ import print_function
import argparse
import sys

import pinject

from lsf_ibutils import metadata
from lsf_ibutils.ibsub.binding_specs import IbsubBindingSpec


def main(argv):
    """Program entry point.

    :param argv: command-line arguments
    :type argv: :class:`list`
    """
    obj_graph = pinject.new_object_graph(binding_specs=[IbsubBindingSpec()])
    return obj_graph.provide(Main)(argv)


class Main(object):
    @pinject.copy_args_to_internal_fields
    def __init__(self, exec_prompts):
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

        arg_parser.parse_args(args=argv[1:])

        print(self._exec_prompts())

        return 0


def entry_point():
    """Zero-argument entry point for use with setuptools/distribute."""
    raise SystemExit(main(sys.argv))


if __name__ == '__main__':
    entry_point()
