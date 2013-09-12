import pytest
parametrize = pytest.mark.parametrize

from lsf_ibutils.ibsub.validate import positive_integer, time_duration


@parametrize(('text', 'valid'), [
    ('notanint', False),
    ('20.4', False),
    ('-20', False),
    ('0', False),
    ('30', True),
])
def test_positive_integer(text, valid):
    assert positive_integer(text) == valid


@parametrize(('text', 'valid'), [
    # These could be farther refined, but I'm not really sure exactly what
    # bsub accepts yet.
    ('11:00', True),
    ('01:54', True),
    ('4:11', True),
    ('45', True),
    ('90', True),
    ('5', True),
    (':34', False),
    ('12:22bcdef', False),
    ('notatime', False),
    ('a4', False),
])
def test_time_duration(text, valid):
    assert time_duration(text) == valid
