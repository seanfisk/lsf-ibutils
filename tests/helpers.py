from mock import MagicMock


def assert_exc_info_msg(exc_info, expected_msg):
    # LHS and RHS intentionally placed so diffs look correct.
    assert expected_msg == str(exc_info.value)


class ConsecutiveRetvalMock(MagicMock):
    """A mock helper which allows easily returning consecutive values when
    called. Use as follows:

    >>> m = ConsecutiveRetvalMock(['first', 'second', 'third'])
    >>> m('a')
    'first'
    >>> m('b')
    'second'
    >>> m('c')
    'third'
    >>> from mock import call
    >>> assert m.mock_calls == [call('a'), call('b'), call('c')]
    """
    def __init__(self, retvals, *args, **kwargs):
        super(ConsecutiveRetvalMock, self).__init__(*args, **kwargs)
        # Invoke name-mangling in order to avoid conflicts with
        # MagicMock behaviors.
        self.__retvals = retvals
        self.__call_count = 0
        self.side_effect = self.__side_effect

    def __side_effect(self, *args, **kwargs):
        """Function which is called to return the correct value."""
        retval = self.__retvals[self.__call_count]
        self.__call_count += 1
        return retval
