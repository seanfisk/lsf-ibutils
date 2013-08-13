from mock import MagicMock
from pytest import fixture

from lsf_ibutils.ibsub.prompts import JobName


@fixture
def mock_simple_prompt():
    return MagicMock()


class TestJobName(object):
    @fixture
    def job_name(self, mock_simple_prompt):
        return JobName(mock_simple_prompt)

    def test_return_value(self, job_name, mock_simple_prompt):
        mock_simple_prompt.return_value = 'awesome'
        assert ('awesome', ['-J', 'awesome']) == job_name({})

    def test_calls_simple_prompt_correctly(self, job_name, mock_simple_prompt):
        job_name({})
        mock_simple_prompt.assert_called_once_with('Job name', required=True)
