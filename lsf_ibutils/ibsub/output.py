""":mod:`lsf_ibutils.ibsub.output` -- Command and script output formatting
"""
# This function has an interesting history of being undocumented, deprecated,
# etc. However, it seems to be portable across Python 2 and 3. See here:
# <http://docs.python.org/2/library/pipes.html#pipes.quote>
from pipes import quote


def build_command(flags):
    """Build a bsub command string from a list of flags.

    :param flags: a list of flags
    :type flags: :class:`list` of :class:`str`
    :return: the command string
    :rtype: :class:`str`
    """
    return ' '.join(['bsub'] + [quote(flag) for flag in flags])
