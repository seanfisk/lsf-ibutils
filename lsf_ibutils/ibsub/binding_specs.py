""":mod:`lsf_ibutils.ibsub.binding_specs` -- pinject setup
"""

from datetime import datetime

from pinject import BindingSpec

from lsf_ibutils.ibsub.prompts import Prompt
from lsf_ibutils.ibsub.input import prompt_for_line, set_completions
from lsf_ibutils.ibsub.output import build_command
from lsf_ibutils.ibsub import validate


class IbsubBindingSpec(BindingSpec):
    def provide_today_datetime(self):
        return datetime.today()

    def provide_prompt_class_list(self):
        return Prompt.__subclasses__()

    def configure(self, bind):
        bind('prompt_for_line', to_instance=prompt_for_line)
        bind('set_completions', to_instance=set_completions)
        bind('build_command', to_instance=build_command)
        bind('validate_positive_integer',
             to_instance=validate.positive_integer)
        bind('validate_time_duration', to_instance=validate.time_duration)
        bind('validate_yes_no', to_instance=validate.yes_no)
