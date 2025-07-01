

from dataclasses import dataclass
from functools import cached_property
import inspect
import typing

@dataclass
class ZutoCmd:
    name : str
    func : typing.Callable
    help : typing.Optional[str] = None

    @cached_property
    def needs_ctx(self) -> bool:
        return "ctx" in inspect.signature(self.func).parameters
    
class ZutoGroup:
    def __init__(self):
        self.cmds : typing.Dict[str, ZutoCmd] = {}
        self.flags : typing.Dict[str, typing.List[typing.Callable]] = {}
    def CMD(self, name : typing.Optional[str] = None, help : typing.Optional[str] = None):
        def decorator(func : typing.Callable):
            if name is None:
                uname = func.__name__
            else:
                uname = name
            self.cmds[uname] = ZutoCmd(name=uname, func=func, help=help)
            return func
        return decorator
    
    def FLAG(self, name : str):
        def decorator(func : typing.Callable):
            self.flags[name] = self.flags.get(name, []) + [func]
            return func
        return decorator
    
    def merge(self, other : "ZutoGroup"):
        for cmd in other.cmds.values():
            if cmd.name in self.cmds:
                raise ValueError(f"Command {cmd.name} already exists")
            self.cmds[cmd.name] = cmd
        for flag, funcs in other.flags.items():
            self.flags[flag] = list(set(self.flags.get(flag, []) + funcs))
        return self 
    