
import copy
import os
from types import MappingProxyType
import json
import toml
import yaml
from resumer.core.action_handle import ActionHandler
from resumer.utils import dump_yaml, presets_path, cache_path, shared_path
from resumer.core.cfgs import RuntimeConfig

class BaseResumer:
    def __init__(self):
        self.__normal_data = {}
        self.__entries = {}

    @property
    def normal_data(self):
        return MappingProxyType(self.__normal_data)
    
    @property
    def entries(self):
        return MappingProxyType(self.__entries)
    
    @property
    def combined(self):
        return {**self.__normal_data, **self.__entries}
    
    def __internal_separate_data_and_entries(self, data : dict):
        normal_data = {}
        entries = {}

        for k, v in data.items():
            if (
                isinstance(v, (list, tuple)) 
                and 
                all(
                    isinstance(x, dict) 
                    for x in v
                )
            ):
                entries[k] = v

            else:
                normal_data[k] = v

        return normal_data, entries

    def load_dict(self, data : dict):
        n, e = self.__internal_separate_data_and_entries(data)
        if len(n) == 0:
            pass
        elif len(self.__normal_data) == 0:
            self.__normal_data = n
        else:
            self.__normal_data.update(n)

        if len(e) == 0:
            pass
        elif len(self.__entries) == 0:
            self.__entries = e
        else:
            for k, v in e.items():
                if k in self.__entries:
                    self.__entries[k].extend(v)
                else:
                    self.__entries[k] = v

    def load_file(self, path : str):
        if path.endswith(".toml"):
            with open(path, "r") as f:
                data = toml.load(f)
                
        elif path.endswith(".json"):
            with open(path, "r") as f:
                data = json.load(f)
        elif path.endswith(".yaml"):
            with open(path, "r") as f:
                data = yaml.safe_load(f)
        else:
            return
        self.load_dict(data)
        
    def load_folder(self, path : str):
        for f in os.listdir(path):
            self.load_file(os.path.join(path, f))

    def filter_entry_count(self, *args, limit : int = 10):
        copied = copy.deepcopy(self)
        for k, v in copied.__entries.items():
            if len(args) == 0 or k in args:
                copied.__entries[k] = v[:limit]

        return copied
    
    def generate_builtin(self, flag : str, runtimeCfg : RuntimeConfig = None):
        if not os.path.exists(os.path.join(presets_path, flag)):
            raise Exception(f"preset {flag} not found")
        
        ah = ActionHandler(runtimeCfg)

        dump_yaml(os.path.join(ah._ActionHandler__tempfolder.name, "input.md"), self.combined)

        with open(os.path.join(presets_path, flag,"config.toml"), "r") as f:
            data = toml.load(f)

        ctx = {}
        ctx["template_dir"] = os.path.join(presets_path, flag)
        ctx["cache_dir"] = cache_path
        ctx["shared_dir"] = shared_path

        ah.generate(data, ctx)

    