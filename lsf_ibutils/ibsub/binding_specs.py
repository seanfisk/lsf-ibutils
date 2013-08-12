""":mod:`lsf_ibutils.ibsub.binding_specs` -- pinject setup
"""

from datetime import datetime

from pinject import BindingSpec

from lsf_ibutils.ibsub.prompts import exec_prompts
from lsf_ibutils.ibsub.input import prompt_for_line, set_completions


class IbsubBindingSpec(BindingSpec):
    def configure(self, bind):
        bind('exec_prompts', to_instance=exec_prompts)
        bind('today_datetime', to_class=datetime.today)
        bind('prompt_for_line', to_instance=prompt_for_line)
        bind('set_completions', to_instance=set_completions)
