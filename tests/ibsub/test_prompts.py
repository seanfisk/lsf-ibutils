from mock import MagicMock, sentinel
from pytest import fixture
import pytest
parametrize = pytest.mark.parametrize

from lsf_ibutils.ibsub.prompts import (
    JobName,
    ProjectCode,
    TasksPerNode,
    WallClockTime,
    QueueName,
    EmailOnFinish,
    EmailOnBegin,
    PromptCommand,
)
# For {Output,Error}FileName
from lsf_ibutils.ibsub import prompts


@fixture
def mock_simple_prompt():
    return MagicMock()


class TestJobName(object):
    @fixture
    def job_name(self, mock_simple_prompt):
        return JobName(mock_simple_prompt)

    def test_return_value(self, job_name, mock_simple_prompt):
        mock_simple_prompt.return_value = sentinel.name
        assert (sentinel.name, ['-J', sentinel.name]) == job_name({})

    def test_calls_simple_prompt_correctly(self, job_name, mock_simple_prompt):
        job_name({})
        mock_simple_prompt.assert_called_once_with('Job name', required=True)


class TestProjectCode(object):
    @fixture
    def project_code(self, mock_simple_prompt):
        return ProjectCode(mock_simple_prompt)

    def test_return_value(self, project_code, mock_simple_prompt):
        mock_simple_prompt.return_value = sentinel.code
        assert (sentinel.code, ['-P', sentinel.code]) == project_code({})

    def test_calls_simple_prompt_correctly(
            self, project_code, mock_simple_prompt):
        project_code({})
        mock_simple_prompt.assert_called_once_with('Project code')


class TestTasksPerNode(object):
    @fixture
    def tasks_per_node(self, mock_simple_prompt):
        return TasksPerNode(mock_simple_prompt, sentinel.validator)

    def test_return_value(self, tasks_per_node, mock_simple_prompt):
        mock_simple_prompt.return_value = '230'
        assert ('230', ['-R', 'span[ptile=230]']) == tasks_per_node({})

    def test_calls_simple_prompt_correctly(
            self, tasks_per_node, mock_simple_prompt):
        tasks_per_node({})
        mock_simple_prompt.assert_called_once_with(
            'Tasks per node',
            format_='positive number',
            validator=sentinel.validator)


class TestWallClockTime(object):
    @fixture
    def wall_clock_time(self, mock_simple_prompt):
        return WallClockTime(mock_simple_prompt, sentinel.validator)

    def test_return_value(self, wall_clock_time, mock_simple_prompt):
        mock_simple_prompt.return_value = sentinel.time
        assert (sentinel.time, ['-W', sentinel.time]) == wall_clock_time({})

    def test_calls_simple_prompt_correctly(
            self, wall_clock_time, mock_simple_prompt):
        wall_clock_time({})
        mock_simple_prompt.assert_called_once_with(
            'Wall clock time limit',
            format_='00:00 for hours or 00 for minutes',
            required=True,
            validator=sentinel.validator)


class TestQueueName(object):
    @fixture
    def mock_get_queues(self):
        return MagicMock()

    @fixture
    def queue_name(self, mock_simple_prompt, mock_get_queues):
        return QueueName(mock_simple_prompt, mock_get_queues)

    def test_return_value(self, queue_name, mock_simple_prompt):
        mock_simple_prompt.return_value = sentinel.queue
        assert (sentinel.queue, ['-q', sentinel.queue]) == queue_name({})

    def test_calls_simple_prompt_correctly(
            self, queue_name, mock_simple_prompt, mock_get_queues):
        mock_get_queues.return_value = sentinel.completions
        queue_name({})
        mock_simple_prompt.assert_called_once_with(
            'Queue',
            required=True,
            validator=queue_name._validator,
            default='regular',
            completions=sentinel.completions)
        mock_get_queues.assert_called_once_with()

    @parametrize(('text', 'valid'), [
        (0, True),
        (9, True),
        (10, False),
        (-1345, False),
        (1e6, False),
        ('notvalid', False),
    ])
    def test_validator(self, queue_name, text, valid, mock_get_queues):
        mock_get_queues.return_value = range(10)
        assert queue_name._validator(text) == valid


class TestOutputErrorFileName(object):
    @fixture(params=['Output', 'Error'])
    def outerr(self, request):
        return request.param

    @fixture
    def file_name(self, mock_simple_prompt, outerr):
        return getattr(prompts, outerr + 'FileName')(mock_simple_prompt)

    def test_return_value(self, outerr, file_name, mock_simple_prompt):
        mock_simple_prompt.return_value = sentinel.file_name
        assert (sentinel.file_name, [
            '-' + outerr[0].lower(), sentinel.file_name]) == file_name({})

    def test_calls_simple_prompt_correctly_without_job_name(
            self, outerr, file_name, mock_simple_prompt):
        file_name({})
        mock_simple_prompt.assert_called_once_with(
            outerr + ' file name',
            default=None)

    def test_calls_simple_prompt_correctly_with_job_name(
            self, outerr, file_name, mock_simple_prompt):
        file_name({JobName: 'my name'})
        mock_simple_prompt.assert_called_once_with(
            outerr + ' file name',
            default='my name.%J.' + outerr[:3].lower())


class TestEmailOnBegin(object):
    @fixture
    def email_on_begin(self, mock_simple_prompt):
        return EmailOnBegin(mock_simple_prompt, sentinel.validator)

    def test_return_value_no(self, email_on_begin, mock_simple_prompt):
        mock_simple_prompt.return_value = 'n'
        assert (None, []) == email_on_begin({})

    def test_return_value_yes(self, email_on_begin, mock_simple_prompt):
        mock_simple_prompt.return_value = 'y'
        assert ('y', ['-B']) == email_on_begin({})

    def test_calls_simple_prompt_correctly(
            self, email_on_begin, mock_simple_prompt):
        email_on_begin({})
        mock_simple_prompt.assert_called_once_with(
            'Notify by email when job begins?',
            format_='y/n',
            default='n',
            validator=sentinel.validator)


class TestEmailOnFinish(object):
    @fixture
    def email_on_finish(self, mock_simple_prompt):
        return EmailOnFinish(mock_simple_prompt, sentinel.validator)

    def test_return_value_no(self, email_on_finish, mock_simple_prompt):
        mock_simple_prompt.return_value = 'n'
        assert (None, []) == email_on_finish({})

    def test_return_value_yes(self, email_on_finish, mock_simple_prompt):
        mock_simple_prompt.return_value = 'y'
        assert ('y', ['-N']) == email_on_finish({})

    def test_calls_simple_prompt_correctly(
            self, email_on_finish, mock_simple_prompt):
        email_on_finish({})
        mock_simple_prompt.assert_called_once_with(
            'Notify by email when job finishes?',
            format_='y/n',
            default='n',
            validator=sentinel.validator)


class TestPromptCommand(object):
    @fixture
    def prompt_command(self, mock_simple_prompt):
        return PromptCommand(mock_simple_prompt)

    def test_return_value(self, prompt_command, mock_simple_prompt):
        mock_simple_prompt.return_value = sentinel.command
        assert prompt_command() == sentinel.command

    def test_calls_simple_prompt_correctly(
            self, prompt_command, mock_simple_prompt):
        prompt_command()
        mock_simple_prompt.assert_called_once_with(
            'Command to run',
            required=True)
