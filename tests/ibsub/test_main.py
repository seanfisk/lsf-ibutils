from pytest import raises, fixture
# The parametrize function is generated, so this doesn't work:
#
#     from pytest.mark import parametrize
#
import pytest
parametrize = pytest.mark.parametrize
from mock import create_autospec

from lsf_ibutils import metadata
from lsf_ibutils.ibsub.main import Main
from lsf_ibutils.ibsub.prompts import exec_prompts


@fixture
def mock_exec_prompts():
    return create_autospec(exec_prompts, spec_set=True)


@fixture
def main(mock_exec_prompts):
    return Main(mock_exec_prompts)


class TestMain(object):
    @parametrize('helparg', ['-h', '--help'])
    def test_help(self, main, helparg, capsys, mock_exec_prompts):
        with raises(SystemExit) as exc_info:
            main(['progname', helparg])
        out, err = capsys.readouterr()
        # Should have printed some sort of usage message. We don't
        # need to explicitly test the content of the message.
        assert 'usage' in out
        # Should have used the program name from the argument
        # vector.
        assert 'progname' in out
        # Should NOT have called exec_prompts.
        assert mock_exec_prompts.call_count == 0
        # Should exit with zero return code.
        assert exc_info.value.code == 0

    @parametrize('versionarg', ['-v', '--version'])
    def test_version(self, main, versionarg, capsys, mock_exec_prompts):
        with raises(SystemExit) as exc_info:
            main(['progname', versionarg])
        out, err = capsys.readouterr()
        # Should print out version.
        assert err == '{0} {1}\n'.format(metadata.project, metadata.version)
        # Should NOT have called exec_prompts.
        assert mock_exec_prompts.call_count == 0
        # Should exit with zero return code.
        assert exc_info.value.code == 0

    def test_calls_exec_prompts(self, main, mock_exec_prompts):
        assert main(['progname']) == 0
        mock_exec_prompts.assert_called_once_with()
