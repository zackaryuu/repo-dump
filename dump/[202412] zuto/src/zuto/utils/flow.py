from zuto.builtin.group import _cmd
from zuto.utils.pyrun import execute_script

def run_oneliner(ctx , script):
    if "ctx" not in script:
        _cmd(script)
    else:
        execute_script(script, ctx)
