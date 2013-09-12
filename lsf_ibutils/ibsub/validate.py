""":mod:`lsf_ibutils.ibsub.validate` -- User input validator functions
"""

import re

TIME_DURATION_RE = re.compile(r'(?:\d\d?:)?\d\d?$')


def positive_integer(text):
    """Validate a positive integer.

    :param text: text to validate
    :type text: :class:`str`
    :return: whether the text was valid
    :rtype: :class:`bool`
    """
    try:
        n = int(text)
    except ValueError:
        return False
    return n > 0


def time_duration(text):
    """Validate a duration of time.

    :param text: text to validate
    :type text: :class:`str`
    :return: whether the text was valid
    :rtype: :class:`bool`
    """
    return bool(TIME_DURATION_RE.match(text))


def yes_no(text):
    """Validate a yes or no question. This function only accepts "y" or "n".

    :param text: text to validate
    :type text: :class:`str`
    :return: whether the text was valid
    :rtype: :class:`bool`
    """
    return text == 'y' or text == 'n'
