from functools import cache
import os
from zuu.stdext_importlib import import_file
from regen import PRESET_PATH
from zuu.util_tempdir import tempdir_op
import toml
import yaml
from zs.api.kvstore import parse_document

@cache
def load_mod(preset):
    presetname = os.path.basename(preset)
    presetMod = import_file(os.path.join(PRESET_PATH, presetname+".py"))
    return presetMod

def load_preset(preset):
    presetMod = load_mod(preset)
    return presetMod.run

def oprun(preset, cwd, profile, data):
    mod = load_mod(preset)
    preset_func = load_preset(preset)
    captures = getattr(mod, "captures", [])
    
    @tempdir_op(cwd, captures=captures)
    def _run(profile, data):
        preset_func(profile, data)

    return _run(profile, data)

def build_input_md(toml_path):
    with open(toml_path, "r") as f:
        filecontent = f.read()
        filecontent = parse_document(filecontent)

    data = toml.loads(filecontent)
    
    with open("input.md", "w") as f:
        f.write("---\n")
        f.write(yaml.safe_dump(data))
        f.write("---\n")
    
    return data