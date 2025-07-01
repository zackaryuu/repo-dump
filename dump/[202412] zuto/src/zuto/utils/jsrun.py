
from zuto.utils.string import fix_indent_level
from subprocess import run

def execute_js(script : str):
    script = fix_indent_level(script)
    # Escape single quotes in the script to prevent syntax errors
    res= run(['node', '-e', script], capture_output=True, text=True)
    if res.stderr:
        raise Exception(res.stderr)
    print(res.stdout)
