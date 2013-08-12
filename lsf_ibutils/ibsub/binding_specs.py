""":mod:`lsf_ibutils.ibsub.binding_specs` -- pinject setup
"""

from datetime import datetime

from pinject import BindingSpec

from lsf_ibutils.ibsub.prompts import exec_prompts


class IbsubBindingSpec(BindingSpec):
    def configure(self, bind):
        bind('exec_prompts', to_instance=exec_prompts)
        bind('today_datetime', to_class=datetime.today)
