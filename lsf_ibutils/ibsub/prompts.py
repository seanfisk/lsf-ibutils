""":mod:`lsf_ibutils.ibsub.prompts` -- List of prompts for flags
"""

from __future__ import print_function

import pinject


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


class ExecPrompts(object):
    @pinject.copy_args_to_internal_fields
    def __init__(self, prompt_class_list, simple_prompt):
        pass

    def __call__(self):
        """Execute all prompts.

        :return: nested list of flags for each prompt
        :rtype: :class:`list` of :class:`list` of :class:`str`
        """
        values = {}
        flags_list = []
        for prompt_class in self._prompt_class_list:
            # XXX TODO Don't manually inject this dependency.
            prompt = prompt_class(self._simple_prompt)

            value, flags = prompt(values)
            values[prompt_class] = value
            flags_list.append(flags)

        return flags_list
