from lsf_ibutils.ibsub.prompts import exec_prompts
from pinject import BindingSpec


class IbsubBindingSpec(BindingSpec):
    def configure(self, bind):
        bind('exec_prompts', to_instance=exec_prompts)
