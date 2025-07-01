
import os
import re


def fix_indent_level(script: str):
    for i, line in enumerate(script.split("\n")):
        if not line:
            continue

        indent_level = len(line) - len(line.lstrip())
        break

    # remove indent level
    script = "\n".join([line[indent_level:] for line in script.split("\n")])
    return script


def extract_global_assign_vars(script: str):
    res =  re.findall(r"\$(\w+)\s*=\s*(.+)", script)
    if res:
        return res
    return []

def parse_environ_vars(script : str):
    res = re.findall(r"\$(\w+)", script)
    if not res:
        return script
    
    for var in res:
        script = script.replace(f"${var}", f"{os.environ.get(var, '(undefined)')}")
    return script


