from mock import create_autospec, call, MagicMock
from pytest import fixture

from lsf_ibutils.ibsub.input import (
    SimplePrompt, prompt_for_line, set_completions)
from tests.helpers import ConsecutiveRetvalMock


class TestSimplePrompt(object):
    @fixture
    def mock_prompt_for_line(self):
        return create_autospec(prompt_for_line, spec_set=True)

    @fixture
    def mock_set_completions(self):
        return create_autospec(set_completions, spec_set=True)

    @fixture
    def simple_prompt(self, mock_prompt_for_line, mock_set_completions):
        return SimplePrompt(mock_prompt_for_line, mock_set_completions)

    def test_prints_basic_prompt(self, simple_prompt, mock_prompt_for_line):
        simple_prompt('AWESOME!!!')
        mock_prompt_for_line.assert_called_once_with('AWESOME!!!: ')

    def test_prints_prompt_with_default(
            self, simple_prompt, mock_prompt_for_line):
        simple_prompt('prompt me', default='hello')
        mock_prompt_for_line.assert_called_once_with('prompt me[hello]: ')

    def test_prints_prompt_with_format(
            self, simple_prompt, mock_prompt_for_line):
        simple_prompt('prompt me', format_='number')
        mock_prompt_for_line.assert_called_once_with('prompt me(number): ')

    def test_prints_prompt_with_default_and_format(
            self, simple_prompt, mock_prompt_for_line):
        simple_prompt('prompt me', format_='number', default='hello')
        mock_prompt_for_line.assert_called_once_with(
            'prompt me(number)[hello]: ')

    def test_returns_entered_value(self, simple_prompt, mock_prompt_for_line):
        mock_prompt_for_line.return_value = 'the user input'
        assert 'the user input' == simple_prompt('not used')

    def test_returns_default(self, simple_prompt, mock_prompt_for_line):
        mock_prompt_for_line.return_value = ''
        assert 'the default' == simple_prompt(
            'not used', default='the default')

    def test_no_default_and_required(self, mock_set_completions, capsys):
        mock_prompt_for_line = ConsecutiveRetvalMock(['', 'value'])
        simple_prompt = SimplePrompt(
            mock_prompt_for_line, mock_set_completions)
        assert 'value' == simple_prompt('a prompt', required=True)
        assert mock_prompt_for_line.mock_calls == [call('a prompt: ')] * 2
        out, err = capsys.readouterr()
        assert '' == out
        assert 'Please enter a value.\n' == err

    def test_validator(self, mock_set_completions, capsys):
        mock_prompt_for_line = ConsecutiveRetvalMock(['wrongvalue', 'value'])
        simple_prompt = SimplePrompt(
            mock_prompt_for_line, mock_set_completions)

        def validator(text):
            return text != 'wrongvalue'
        assert 'value' == simple_prompt('a prompt', validator=validator)
        assert mock_prompt_for_line.mock_calls == [call('a prompt: ')] * 2
        out, err = capsys.readouterr()
        assert '' == out
        assert 'Please enter the correct format.\n' == err

    def test_default_is_not_validated(
            self, simple_prompt, mock_prompt_for_line):
        mock_prompt_for_line.return_value = ''
        mock_validator = MagicMock()
        assert 'thedefault' == simple_prompt(
            'hello', default='thedefault', validator=mock_validator)
        assert mock_validator.call_count == 0

    def test_default_and_required(self, simple_prompt, mock_prompt_for_line):
        mock_prompt_for_line.return_value = ''
        assert 'thedefault' == simple_prompt(
            'hello', default='thedefault', required=True)

    def test_no_default_and_not_required(
            self, simple_prompt, mock_prompt_for_line):
        mock_prompt_for_line.return_value = ''
        assert None == simple_prompt('hello')

    def test_sets_completions(self, simple_prompt, mock_set_completions):
        completions = ['abc', 'def', 'ghi']
        simple_prompt('not used', completions=completions)
        mock_set_completions.assert_called_once_with(completions)
