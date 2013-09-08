""":mod:`lsf_ibutils.ibsub.input` -- User input functions
"""

from __future__ import print_function
import sys
# Uses GNU readline on UNIX-like operating systems, pyreadline on Windows.
import readline

import pinject


class SimplePrompt(object):
    @pinject.copy_args_to_internal_fields
    def __init__(self, prompt_for_line, set_completions):
        pass

    def __call__(self, message, required=False, format_=None, validator=None,
                 default=None, completions=[]):
        """Prompt the user based on the passed options.

        :param message: the prompt message to display to the user
        :type message: :class:`str`
        :param required: whether this flag is required
        :type required: :class:`bool`
        :param format_: hint to display to the user indicating the text \
        format,  e.g. 'number'
        :type format_: :class:`str`
        :param validator: a function returning a :class:`bool` which \
        indicates whether the field is valid, receives the user-entered string
        :type validator: :class:`function`
        :param default: this flag's default value
        :type default: :class:`str`
        :param completions: a list of completions for this prompt
        :type completions: :class:`list` of :class:`str`
        :return: the user-entered text
        :rtype: :class:`str`
        """
        # Build the prompt text.
        prompt_text_list = [message]
        if format_ is not None:
            prompt_text_list.append('({0})'.format(format_))
        if default is not None:
            prompt_text_list.append('[{0}]'.format(default))
        prompt_text_list.append(': ')
        prompt_text = ''.join(prompt_text_list)

        # Set the completions.
        self._set_completions(completions)

        # Prompt for the value.
        while True:
            text = self._prompt_for_line(prompt_text)
            if text == '':
                # The first if and elif are actually redundant because
                # `default' has a default of None anyway. But it is written
                # this way for the purpose of clear and explicit code.
                if default is not None:
                    result = default
                    break
                elif not required:
                    result = None
                    break
                else:
                    print('Please enter a value.', file=sys.stderr)
            elif validator is None or validator(text):
                result = text
                break
            else:
                print('Please enter the correct format.', file=sys.stderr)
        return result


def prompt_for_line(prompt):
    """Easily accept input. When <Ctrl-D> (UNIX-like) or <Ctrl-Z> +
    <Enter> (Windows) is pressed to send the EOF character, just
    return an empty string instead.

    :param prompt: the prompt to display
    :type prompt: :class:`str`
    :return: the user's input text
    :rtype: :class:`str`
    """
    # raw_input by default prints to stdout, but we want to print to stderr.
    sys.stdout = sys.stderr
    try:
        # If input is being piped or redirected in, there is no need to print
        # the prompts.
        if not sys.stdin.isatty():
            prompt = ''
        return raw_input(prompt)
    except EOFError:
        # Since the user didn't press Enter, a newline wouldn't be printed to
        # the screen. Print one here so the next line looks correct.
        print(file=sys.stderr)
        # Simplify catching this to just returning an empty string.
        return ''
    finally:
        sys.stdout = sys.__stdout__


# Completion handling

_completions = []


def set_completions(completions):
    """Set global readline completions.

    :param completions: list of completions
    :type completions: :class:`list` of :class:`str`
    """
    # Set the contents of the list.
    _completions[:] = completions


def _readline_completer(text, state):
    # This is a clever way to return the correction completion for
    # the "state". Basically, the "state" is the amount of times
    # tab has been pressed. This code decrements state to find the
    # nth completion starting with the text.
    for completion in _completions:
        if completion.lower().startswith(text.lower()):
            if state == 0:
                return completion
            else:
                state -= 1

readline.parse_and_bind('tab: complete')
readline.set_completer(_readline_completer)
