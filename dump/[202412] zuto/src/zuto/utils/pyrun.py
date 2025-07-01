
import re
import os

from zuto.utils.string import extract_global_assign_vars, fix_indent_level

def check_script_restrictions(script : str):
    for line in script.split("\n"):
        if line.startswith("import"):
            raise ValueError("Imports are not allowed in scripts")
        
        if line.startswith("from"):
            raise ValueError("From imports are not allowed in scripts")
        
        if "__import__" in line:
            raise ValueError("__import__ is not allowed in scripts")
        


def execute_script(script : str, ctx):
    from zuto.core.ctx import ZutoCtx
    ctx : ZutoCtx = ctx
    
    if not ctx.is_unsafe:
        check_script_restrictions(script)

    #global setup
    passobj = ctx if ctx.is_unsafe else ctx.safe
    gvars = {
        "ctx" : passobj
    }

    bkup_env = os.environ.copy()
    gvars.update(os.environ)

    # local setup
    lvars = {}
    
    gassigns = extract_global_assign_vars(script)
    
    # replace $var to var
    script = re.sub(r"\$(\w+)", lambda m: m.group(1).upper(), script)
    script = fix_indent_level(script)

    exec(script, gvars, lvars)
    
    gvars.pop("ctx")

    # apply global assigns
    for k, v in bkup_env.items():
        k = k.upper()
        if gvars[k] != v:
            os.environ[k] = gvars[k]

    for ga in gassigns:
        ga0 = ga[0].upper()

        os.environ[ga0] = lvars[ga0]

