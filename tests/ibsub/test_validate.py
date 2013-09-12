import pytest
parametrize = pytest.mark.parametrize

from lsf_ibutils.ibsub import validate


@parametrize(('text', 'valid'), [
    ('notanint', False),
    ('20.4', False),
    ('-20', False),
    ('0', False),
    ('30', True),
])
def test_positive_integer(text, valid):
    assert validate.positive_integer(text) == valid


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
    assert validate.time_duration(text) == valid


@parametrize(('text', 'valid'), [
    ('y', True),
    ('n', True),
    ('Y', False),
    ('N', False),
    ('yes', False),
    ('no', False),
    ('Yes', False),
    ('No', False),
    ('yup', False),
    ('wrong', False),
])
def test_yes_no(text, valid):
    assert validate.yes_no(text) == valid
