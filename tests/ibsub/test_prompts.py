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
        return TasksPerNode(mock_simple_prompt)

    def test_return_value(self, tasks_per_node, mock_simple_prompt):
        mock_simple_prompt.return_value = '230'
        assert ('230', ['-R', 'span[ptile=230]']) == tasks_per_node({})

    def test_calls_simple_prompt_correctly(
            self, tasks_per_node, mock_simple_prompt):
        tasks_per_node({})
        mock_simple_prompt.assert_called_once_with(
            'Tasks per node',
            format_='positive number',
            validator=tasks_per_node._validator)

    @parametrize(('text', 'valid'), [
        ('notanint', False),
        ('20.4', False),
        ('-20', False),
        ('0', False),
        ('30', True),
    ])
    def test_validator(self, tasks_per_node, text, valid):
        assert tasks_per_node._validator(text) == valid


class TestWallClockTime(object):
    @fixture
    def wall_clock_time(self, mock_simple_prompt):
        return WallClockTime(mock_simple_prompt)

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
            validator=wall_clock_time._validator)

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
    def test_validator(self, wall_clock_time, text, valid):
        assert wall_clock_time._validator(text) == valid


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
