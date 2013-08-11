from lsf_ibutils.ibsub.output import build_command


class TestBuildCommand(object):
    def test_simple(self):
        assert (build_command(
            ['-J', 'awesomename', '-P', 'awesomeproj',
             '-n', '10', 'command']) ==
            'bsub -J awesomename -P awesomeproj -n 10 command')

    def test_ptile(self):
        assert (build_command(['-R', 'span[ptile=n]', 'command']) ==
                "bsub -R 'span[ptile=n]' command")

    def test_spaces(self):
        assert (build_command(
            ['-J', 'job name', '-P', 'proj name',
             '-q', 'queue with spaces', 'command with spaces']) ==
            "bsub -J 'job name' -P 'proj name' "
            "-q 'queue with spaces' 'command with spaces'")

    def test_special_chars(self):
        # Mostly just a test that pipes.quote is working properly.
        assert (build_command(
            ['-J', "job' nam[e]", '-P', 'pr{oj n}ame \\escape',
             '-q', '`tick` $(param sub)', '"difficult \\n command"']) ==
            "bsub -J 'job'\"'\"' nam[e]' -P 'pr{oj n}ame \escape' "
            "-q '`tick` $(param sub)' '\"difficult \\n command\"'")
