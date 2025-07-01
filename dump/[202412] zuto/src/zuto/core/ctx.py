from functools import cached_property
import logging
from types import MappingProxyType
import typing
from zuto.builtin.spec import JobSpec
from zuto.core._flagHandle import CtxFlagHandle
from zuto.core._imports import CtxImports
from zuto.core._meta import CtxMeta
from zuto.core._vars import CtxVars
from zuto.core.group import ZutoGroup
from zuto.builtin.group import builtinGroup
from zuto.core.part import ZutoPart

class CtxJobs:
    def __init__(self, ctx : "ZutoCtx"):
        self.__ctx = ctx
        self.__job_seq : typing.List[JobSpec] = []
        self.__job_index : int = 0
        self._goto_index : int = None

    def _push(self, job : JobSpec):
        self.__job_seq.append(job)
    
    @property
    def current(self) -> JobSpec:
        if self.__job_index >= len(self.__job_seq):
            return None
        return self.__job_seq[self.__job_index]
    
    @property
    def seq(self) -> typing.List[JobSpec]:
        return list(self.__job_seq)
    
    def _pop(self, job : JobSpec):
        try:
            self.__job_seq.remove(job)
        except ValueError:
            raise ValueError(f"Job {job} not found in sequence")

    def next(self):
        self.__ctx.flags.set("NEXT")

    def _next(self):
        self.__job_index += 1

    def goto(self, index : typing.Optional[int] = None, job : typing.Optional[JobSpec] = None):
        if index:
            assert index >= 0 and index < len(self.__job_seq)
        elif job:
            index = self.__job_seq.index(job)
        else:
            raise ValueError("No job specified")
        
        self._goto_index = index
        self.__ctx.flags.set("GOTO")

    def _goto(self):
        self.__job_index = self._goto_index
       
    @property
    def index(self) -> int:
        return self.__job_index

    def skip(self):
        self.__ctx.flags.set("SKIP")

class ZutoCtx:
    imports = CtxImports

    BUILTIN_FLAGS = [
        "UNSAFE",
        "SKIP",
        "EXIT",
        "ERROR",
        "SUCCESS",
        "FAIL",
        "THROW"
    ]

    def __init__(self, specs : typing.List[ZutoPart]) -> None:
        self._reset()
        self.__specs = specs
        self.__jobs = CtxJobs(self)

    @property
    def _specs(self) -> typing.List[ZutoPart]:
        return self.__specs
    
    @cached_property
    def specs(self) -> typing.List[dict]:
        return [MappingProxyType(spec.model_dump()) for spec in self._specs]

    @property
    def group(self) -> ZutoGroup:
        return self.__group
    
    @property
    def meta(self) -> CtxMeta:
        return self.__meta
    
    @property
    def flow(self) -> CtxJobs:
        return self.__jobs

    def _reset(self):
        self.__group = ZutoGroup().merge(builtinGroup)
        self.__flag_handle = CtxFlagHandle()
        self.__meta = CtxMeta()
        self.__jobs = CtxJobs(self)

    # flags
    @property
    def flags(self) -> CtxFlagHandle:
        return self.__flag_handle

    @property
    def is_unsafe(self) -> bool:
        return self.__flag_handle.has("UNSAFE")

    def unsafe(self):
        self.flags.set("UNSAFE")

    @cached_property
    def safe(self) -> "ZutoCtxProxy":
        return ZutoCtxProxy(self)
    
    def _invoke(self, data : dict):
        item = data.popitem()
        return self.invoke(item[0], *[item[1]], **data)

    def invoke(self, name : str, *args, **kwargs):
        cmd = self.group.cmds[name]
        logging.info(f"Invoking {name}")
        
        if cmd.needs_ctx:
            logging.debug(f"Command {name} needs context")
            return cmd.func(self, *args, **kwargs)
        else:
            return cmd.func(*args, **kwargs)

    def eval(self, expr : str) -> bool:
        if self.is_unsafe:
            vars = {"ctx" : self}
        else:
            vars = {"ctx" : self.safe}
        res = eval(expr, vars, {})
        return bool(res)
    
    def console(self, string : str):
        print(string)

    @cached_property
    def vars(self) -> CtxVars:
        return CtxVars()
    
    def _reconcile_flags(self):
        for flag, funcs in self.group.flags.items():
            if self.__flag_handle.has(flag):
                for func in funcs:
                    func(self)

class ZutoCtxProxy:
    _forbidden_attrs = [
        "group",
        "invoke",
        "eval",
        "safe"
    ]

    def __init__(self, ctx : ZutoCtx):
        self.__ctx = ctx

    def __getattr__(self, name : str) -> typing.Any:
        if name == "__ctx":
            return super().__getattr__(name)
        if name in self._forbidden_attrs:
            raise AttributeError(f"{name} is forbidden")
        if name.startswith("_"):
            raise AttributeError(f"{name} is forbidden")
        return getattr(self.__ctx, name)

