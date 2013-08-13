""":mod:`lsf_ibutils.ibsub.binding_specs` -- pinject setup
"""

from datetime import datetime

from pinject import BindingSpec

from lsf_ibutils.ibsub.prompts import Prompt
from lsf_ibutils.ibsub.input import prompt_for_line, set_completions


class IbsubBindingSpec(BindingSpec):
    def provide_today_datetime(self):
        return datetime.today()

    def provide_prompt_class_list(self):
        return Prompt.__subclasses__()

    def configure(self, bind):
        bind('prompt_for_line', to_instance=prompt_for_line)
        bind('set_completions', to_instance=set_completions)
