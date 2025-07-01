
import logging
import os
from zuto.core.group import ZutoGroup
from zuu.subprocess_ import execute

from zuto.utils.pyrun import execute_script
from zuto.utils.jsrun import execute_js
from zuto.utils.string import parse_environ_vars

builtinGroup = ZutoGroup()

@builtinGroup.CMD("cmd")
def _cmd(cmd: str, detached: bool = False, d: bool = False):
    cmd = parse_environ_vars(cmd)
    if detached or d:
        execute(*cmd.split(" "))
    else:
        os.system(cmd)
    
@builtinGroup.CMD("pwsh")
def _pwsh(cmd: str):
    _cmd(f"pwsh -Command {cmd}")

@builtinGroup.CMD("py")
def _py(ctx, script : str):
    execute_script(script, ctx)
    
@builtinGroup.CMD("js")
def _js(script : str):
    execute_js(script)

@builtinGroup.CMD("env")
def _env(keyval : str):
    if keyval.startswith("~"):
        logging.debug(f"Removing environment variable: {keyval[1:]}")
        os.environ.pop(keyval[1:])
        return

    key, val = keyval.split("=")
    os.environ[key] = val

    logging.debug(f"Setting environment variable: {key}={val}")
    

@builtinGroup.FLAG("EXIT")
def _exit(ctx):
    exit(0)

@builtinGroup.FLAG("SKIP")
def _skip(ctx):
    ctx.flow._skip()

@builtinGroup.FLAG("GOTO")
def _goto(ctx):
    ctx.flow._goto()

@builtinGroup.FLAG("GOTO")
def _goto(ctx):
    ctx.flow._goto()

