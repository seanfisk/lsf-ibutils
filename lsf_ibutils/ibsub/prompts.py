""":mod:`lsf_ibutils.ibsub.prompts` -- List of prompts for flags
"""

from __future__ import print_function
import os
import subprocess
from tempfile import TemporaryFile

import pinject

from lsf_ibutils import ibsub

# The two options for specifying flags are declarative and imperative. After
# trying the declarative approach initially, we made the decision that no
# amount of custom options for the declarative approach would allow it to be as
# customized as some of the arguments needed. Instead, we opted for the
# imperative approach, with each function built up from smaller, private
# library functions.


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


class TasksPerJob(Prompt):
    """Prompt for the number total tasks in this job."""
    def __init__(self, simple_prompt, validate_positive_integer):
        self._simple_prompt = simple_prompt
        self._validator = validate_positive_integer

    def __call__(self, values):
        text = self._simple_prompt(
            'Tasks per job',
            format_='positive number',
            required=True,
            validator=self._validator)
        return (text, ['-n', text])


class TasksPerNode(Prompt):
    """Prompt for the number of MPI tasks to run on each node."""
    def __init__(self, simple_prompt, validate_positive_integer):
        self._simple_prompt = simple_prompt
        self._validator = validate_positive_integer

    def __call__(self, values):
        text = self._simple_prompt(
            'Tasks per node',
            format_='positive number',
            validator=self._validator)
        return (text, ['-R', 'span[ptile={0}]'.format(text)])


class WallClockTime(Prompt):
    """Prompt for the wall clock time limit of the task, in seconds."""
    def __init__(self, simple_prompt, validate_time_duration):
        self._simple_prompt = simple_prompt
        self._validator = validate_time_duration

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
        # TODO Remove this validator from inside this class
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


class EmailOnBegin(Prompt):
    """Prompt whether to send an email to the user when the job begins."""
    def __init__(self, simple_prompt, validate_yes_no):
        self._simple_prompt = simple_prompt
        self._validator = validate_yes_no

    def __call__(self, values):
        text = self._simple_prompt(
            'Notify by email when job begins?',
            format_='y/n',
            default='n',
            validator=self._validator)
        if text == 'n':
            value = None
            flags = []
        else:
            value = text
            flags = ['-B']
        return (value, flags)


class EmailOnFinish(Prompt):
    """Prompt whether to send an email to the user when the job finishes."""
    def __init__(self, simple_prompt, validate_yes_no):
        self._simple_prompt = simple_prompt
        self._validator = validate_yes_no

    def __call__(self, values):
        text = self._simple_prompt(
            'Notify by email when job finishes?',
            format_='y/n',
            default='n',
            validator=self._validator)
        if text == 'n':
            value = None
            flags = []
        else:
            value = text
            flags = ['-N']
        return (value, flags)


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
