""":mod:`lsf_ibutils.ibsub.prompts` -- List of prompts for flags
"""

from __future__ import print_function
import re
import os
import subprocess

import pinject

from lsf_ibutils import ibsub

# The two options for specifying flags are declarative and imperative. After
# trying the declarative approach initially, we made the decision that no
# amount of custom options for the declarative approach would allow it to be as
# customized as some of the arguments needed. Instead, we opted for the
# imperative approach, with each function built up from smaller, private
# library functions.

WALL_CLOCK_RE = re.compile(r'(?:\d\d?:)?\d\d?$')


class Prompt(object):
    """Class from which other prompts should inherit."""
    @pinject.copy_args_to_internal_fields
    def __init__(self, simple_prompt):
        pass

    def __call__(self, values):
        """Execute the prompt.

        :param values: a dictionary of class name to previously read value
        :type values: :class:`dict`
        :return: a tuple of (value, flags)
        :rtype: :class:`tuple` of (:class:`str`, :class:`list` of :class:`str`)
        """
        raise NotImplementedError()


class JobName(Prompt):
    """Prompt for the name of the job."""
    def __call__(self, values):
        text = self._simple_prompt('Job name', required=True)
        return (text, ['-J', text])


class ProjectCode(Prompt):
    """Prompt for the project code, usually the same as the user's group."""
    def __call__(self, values):
        text = self._simple_prompt('Project code')
        return (text, ['-P', text])


class TasksPerNode(Prompt):
    """Prompt for the number of MPI tasks to run on each node."""
    def _validator(self, text):
        try:
            n = int(text)
        except ValueError:
            return False
        return n > 0

    def __call__(self, values):
        text = self._simple_prompt(
            'Tasks per node',
            format_='positive number',
            validator=self._validator)
        return (text, ['-R', 'span[ptile={0}]'.format(text)])


class WallClockTime(Prompt):
    """Prompt for the wall clock time limit of the task, in seconds."""
    def _validator(self, text):
        return bool(WALL_CLOCK_RE.match(text))

    def __call__(self, values):
        text = self._simple_prompt(
            'Wall clock time limit',
            format_='00:00 for hours or 00 for minutes',
            required=True,
            validator=self._validator)
        return (text, ['-W', text])


class QueueName(Prompt):
    """Prompt for the job queue name."""
    @pinject.copy_args_to_internal_fields
    def __init__(self, simple_prompt, get_queues):
        pass

    def _validator(self, text):
        return text in self._get_queues()

    def __call__(self, args_thus_far):
        text = self._simple_prompt(
            'Queue',
            required=True,
            validator=self._validator,
            # This is hard-coded to our particular machine, but it seems like a
            # reasonable default everywhere.
            default='regular',
            completions=self._get_queues(),
        )
        return (text, ['-q', text])


class OutputFileName(Prompt):
    def __call__(self, values):
        try:
            default = '{0}.%J.out'.format(values[JobName])
        except KeyError:
            default = None
        text = self._simple_prompt(
            'Output file name',
            default=default
        )
        return (text, ['-o', text])


class ErrorFileName(Prompt):
    def __call__(self, values):
        try:
            default = '{0}.%J.err'.format(values[JobName])
        except KeyError:
            default = None
        text = self._simple_prompt(
            'Error file name',
            default=default
        )
        return (text, ['-e', text])


class PromptCommand(object):
    @pinject.copy_args_to_internal_fields
    def __init__(self, simple_prompt):
        pass

    def __call__(self):
        return self._simple_prompt('Command to run', required=True)


class ExecPrompts(object):
    @pinject.copy_args_to_internal_fields
    def __init__(self, prompt_class_list, simple_prompt):
        pass

    def __call__(self):
        """Execute all prompts.

        :return: nested list of flags for each prompt
        :rtype: :class:`list` of :class:`list` of :class:`str`
        """
        # XXX TODO Untested
        values = {}
        flags_list = []
        for prompt_class in self._prompt_class_list:
            prompt = ibsub.obj_graph.provide(prompt_class)
            value, flags = prompt(values)
            if value is None:
                continue
            values[prompt_class] = value
            flags_list.append(flags)
        return flags_list


class GetQueues(object):
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
            output = subprocess.check_output(bqueues_args)
            # Strip off the first line, which is a header.
            lines = output.splitlines()[1:]
            for line in lines:
                queue = line.split()[0]
                queues.append(queue)
        except subprocess.CalledProcessError:
            pass
        except OSError:
            pass
        # If the bqueues subprocess bombs out on an error, just ignore it.  The
        # program can be useful even without completions. If we don't have
        # bqueues our program should not crash.

        # Memoize the completions. We also memoize an empty list of completions
        # because if it didn't work a second ago, it's not likely to work now.
        self._queue_cache = queues

        return queues
