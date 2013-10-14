""":mod:`lsf_ibutils.ibsub.completers` -- Completion functions for prompts
"""

import os
import subprocess
from tempfile import TemporaryFile


class GetQueueCompletions(object):
    def __init__(self):
        self._queue_cache = None

    def __call__(self):
        # XXX TODO Untested

        # Retrieve memoized queue list, if it exists.
        if self._queue_cache is not None:
            return self._queue_cache

        bqueues_args = ['bqueues']
        current_user = os.getenv('USER')
        if current_user is not None:
            # These arguments will get allowed queues for the current user.
            bqueues_args += ['-u', current_user]
        queues = []
        with TemporaryFile() as output_file:
            try:
                subprocess.check_call(bqueues_args, stdout=output_file)
            except (subprocess.CalledProcessError, OSError):
                # If the bqueues subprocess bombs out on an error, just ignore
                # it.  The program can be useful even without completions. If
                # we don't have bqueues our program should not crash.
                return queues

            # Jump to beginning of file.
            output_file.seek(0)
            try:
                # Strip off the first line, which is a header. If this doesn't
                # exist, it will raise a StopIteration.
                next(output_file)
            except StopIteration:
                # Raised by the call to next() if there are no lines in the
                # file.
                return queues
            # Grab queue names. Process the file line-by-line instead of
            # reading the whole file into memory. Should be more
            # memory-efficient.
            for line in output_file:
                tokens = line.split()
                if len(tokens) > 0:
                    queues.append(tokens[0])

        # Memoize the completions. We also memoize an empty list of completions
        # because if it didn't work a second ago, it's not likely to work now.
        self._queue_cache = queues

        return queues


class GetGroupCompletions(object):
    def __init__(self):
        self._group_cache = None

    def __call__(self):
        # XXX TODO Untested

        # Retrieve memoized group list, if it exists.
        if self._group_cache is not None:
            return self._group_cache

        groups_containing_user = []
        current_user = os.getenv('USER')
        if current_user is None:
            # If we can't detect the current user, just give up. Returning the
            # entire list of groups produced by `bugroup' would be too many
            # group completions.
            return groups_containing_user

        # Process the file line-by-line instead of reading the whole file into
        # memory. Should be more memory-efficient.
        with TemporaryFile() as output_file:
            try:
                subprocess.check_call(['bugroup'], stdout=output_file)
            except (subprocess.CalledProcessError, OSError):
                # If the bqueues subprocess bombs out on an error, just ignore
                # it.  The program can be useful even without completions. If
                # we don't have bqueues our program should not crash.
                return groups_containing_user

            # Jump to beginning of file.
            output_file.seek(0)

            try:
                # Strip off the first line, which is a header. If this doesn't
                # exist, it will raise a StopIteration.
                next(output_file)
            except StopIteration:
                # Raised by the call to next() if there are no lines in the
                # file.
                return groups_containing_user

            # Parse group names to which the user belongs. Process the file
            # line-by-line instead of reading the whole file into
            # memory. Should be more memory-efficient.
            for line in output_file:
                tokens = line.split()
                group_name = tokens[0]
                group_members = tokens[1:]
                if current_user in group_members:
                    groups_containing_user.append(group_name)

        # Memoize the completions. We also memoize an empty list of completions
        # because if it didn't work a second ago, it's not likely to work now.
        self._group_cache = groups_containing_user

        return groups_containing_user
