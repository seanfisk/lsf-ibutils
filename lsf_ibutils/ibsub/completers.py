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

        # Retrieve memoized queue list, if they exist.
        if self._queue_cache is not None:
            return self._queue_cache

        bqueues_args = ['bqueues']
        current_user = os.getenv('USER')
        if current_user is not None:
            # These arguments will get allowed queues for the current user.
            bqueues_args += ['-u', current_user]
        queues = []
        try:
            # Process the file line-by-line instead of reading the whole file
            # into memory. Should be more memory-efficient.
            with TemporaryFile() as output_file:
                subprocess.check_call(bqueues_args, stdout=output_file)
                # NOTE: If the subprocess call bombs, the file still gets
                # closed. Yay Python for doing the right thing!

                # Jump to beginning of file.
                output_file.seek(0)
                # Strip off the first line, which is a header. If this doesn't
                # exist, it will raise a StopIteration.
                next(output_file)
                # Grab queue names.
                for line in output_file:
                    tokens = line.split()
                    if len(tokens) > 0:
                        queues.append(tokens[0])
        except subprocess.CalledProcessError:
            pass
        except OSError:
            pass
        except StopIteration:
            # Raised by the call to next() if there are no lines in the file.
            pass
        # If the bqueues subprocess bombs out on an error, just ignore it.  The
        # program can be useful even without completions. If we don't have
        # bqueues our program should not crash.

        # Memoize the completions. We also memoize an empty list of completions
        # because if it didn't work a second ago, it's not likely to work now.
        self._queue_cache = queues

        return queues
