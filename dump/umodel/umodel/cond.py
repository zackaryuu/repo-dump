
from dataclasses import dataclass
import dataclasses
import logging
import typing

@dataclass(frozen=True)
class CondField:
    value : typing.Any = None
    funcs : typing.List[typing.Callable] = dataclasses.field(default_factory=list)
    chained_funcs : bool = False
    typ : typing.Type = None
    # range
    range : typing.Iterable = None
    min : typing.Any = None
    max : typing.Any = None 
    min_inclusive : bool = True
    max_inclusive : bool = True
    # if iterable
    min_len : int = None
    max_len : int = None

    @property
    def stats(self):
        return {
            "value": self.value,
            "funcs": self.funcs,
            "chained_funcs": self.chained_funcs,
            "typ": self.typ,
            "range": self.range,
            "min": self.min,
            "max": self.max,
            "min_inclusive": self.min_inclusive,
            "max_inclusive": self.max_inclusive,
            "min_len": self.min_len,
            "max_len": self.max_len,
        }

    def __post_init__(self):
        # check func

        if isinstance(self.funcs, typing.Iterable):
            for func in self.funcs:
                if not callable(func):
                    func : typing.Callable
                    raise Exception(f"func: {func.__name__} is not callable")
        
        # check range
        if self.range is not None and (self.min is not None or self.max is not None):
            raise Exception("range and min/max cannot be both set")

        # 

        if not isinstance(self.value, typing.Iterable) and (self.min_len is not None or self.max_len is not None):
            raise Exception("min/max_len only works with iterable")

        if not isinstance(typing.get_origin(self.typ), typing.Iterable) and (self.min_len is not None or self.max_len is not None):
            raise Exception("min/max_len only works with iterable")
        
        # iterable cannot have range
        if self.range is not None and isinstance(typing.get_origin(self.typ), typing.Iterable):
            raise Exception("range only works with non-iterable")
        #
        if self.funcs is not None and not isinstance(self.funcs, list):
            object.__setattr__(self, "funcs", [self.funcs])

    def match_len(self, value) -> bool:
        if self.min_len is not None and len(value) < self.min_len:
            return False

        if self.max_len is not None and len(value) > self.max_len:
            return False

        return True

    def match_range(self, value) -> bool:
        if self.range is None and self.min is None and self.max is None:
            return True

        xmin = self.min
        xmax = self.max

        if self.range and len(self.range) == 2:
            xmin, xmax = self.range

        if len(self.range) != 2 and value not in self.range:
            return False
        
        if xmin is not None and self.min_inclusive and value < xmin:
            return False

        if xmax is not None and self.max_inclusive and value > xmax:
            return False

        if xmin is not None and not self.min_inclusive and value <= xmin:
            return False
        
        if xmax is not None and not self.max_inclusive and value >= xmax:
            return False
        
        return True 

    def match_type(self, value) -> bool:
        if value is None and not isinstance(self.typ, type(None)):
            return True

        if  self.typ is None:
            return True

        typing_match = typing.get_origin(self.typ) is not None and isinstance(value, typing.get_origin(self.typ))
        type_match = isinstance(value, self.typ)
        is_iterable = isinstance(value, typing.Iterable)
        sub_element_match = is_iterable and all(isinstance(v, typing.get_args(self.typ)) for v in value)

        if not typing_match and not type_match:
            return False
        
        if is_iterable and not sub_element_match and not isinstance(value, str):
            return False

        return True

    def _match_chained_funcs(self, value) -> typing.Tuple[bool, typing.Any]:
        func_res = value
        for func in self.funcs:
            func_res = func(func_res)
            if func_res == False:
                return False, func.__name__

        return True, func_res
        

    def match_funcs(self, value)-> typing.Tuple[bool, typing.Dict]:
        if self.funcs is None or len(self.funcs) == 0:
            return True, None

        if len(self.funcs) == 1:
            func_res = self.funcs[0](value)
            if func_res == False:
                return False, None
            return True, None

        if not self.chained_funcs:
            ret_func_val = {}
            for func in self.funcs:
                ret_func_val[func.__name__] = func(value)
            if not all(func_val != False for func_val in ret_func_val.values()):
                return False, ret_func_val
            return True, ret_func_val

        return self._match_chained_funcs(value)

    def _match(self, value) -> typing.Tuple[bool, typing.Dict]:
        try:
            funcs_ret = None
            if self.value is not None and value != self.value:
                return False, funcs_ret

            if not self.match_type(value):
                return False, funcs_ret

            if not (ret := self.match_funcs(value))[0]:
                return ret
            
            funcs_ret = ret[1]

            if not self.match_range(value):
                return False, funcs_ret

            if not self.match_len(value):
                return False, funcs_ret

            return True, funcs_ret
        except Exception as e:
            logging.error(e)
            return False, funcs_ret

    def match(self, value) -> bool:
        return self._match(value)[0]
        

    def match_all(self, *args, allf : bool = False):
        if allf:
            return all(self.match(arg) for arg in args)
        
        ret = {}
        for arg in args:
            ret[str(arg)] = self.match(arg)
        
        return ret

    @classmethod
    def cmatch(cls, value,args : typing.Union[list, dict, typing.Any]) -> bool:
        if not args or len(args) == 0:
            return True
        
        if isinstance(args, dict):
            return cls(**args).match(value)
        elif isinstance(args, list):
            return cls(*args).match(value)
        else:
            return cls(value=args).match(value)


    @classmethod
    def create(cls, *args, 
        value=None, 
        funcs=None, 
        typ=None,
        range=None, 
        min=None, 
        max=None, 
        min_inclusive=True, 
        max_inclusive=True, 
        min_len=None, 
        max_len=None,
        chained_funcs=False,
    ):
        args = set(args)

        for arg in args:
            if isinstance(arg, type):
                typ = arg
            elif isinstance(arg, typing.Iterable):
                range = arg
            elif isinstance(arg, typing.Callable):
                if not isinstance(funcs, typing.List):
                    funcs = []

                funcs.append(arg)
            else:
                value = arg

        return cls(
            value=value,
            funcs=funcs,
            typ=typ,
            range=range,
            min=min,
            max=max,
            min_inclusive=min_inclusive,
            max_inclusive=max_inclusive,
            min_len=min_len,
            max_len=max_len,
            chained_funcs=chained_funcs,
        )

            
@dataclass(init=False, frozen=True)
class CondLex:
    def __init__(self, **kwargs) -> None:
        object.__setattr__(self, "__conds__", {})
        self.__conds__ : typing.Dict[str, CondField] 

        for key, value in kwargs.items():
            if value is None:
                raise Exception("value cannot be None")

            if isinstance(value, (set, list, tuple)):
                self.__conds__[key] = CondField.create(*value)
            elif isinstance(value, CondField):
                self.__conds__[key] = value
            else:
                self.__conds__[key] = CondField.create(value=value)

    def match(self, **kwargs) -> bool:
        for key, value in kwargs.items():
            if key not in self.__conds__:
                continue

            if not self.__conds__[key].match(value):
                return False

        return True

    @classmethod
    def cmatch(cls, data, **kwargs):
        if not isinstance(data, dict):
            raise Exception("data must be dict")

        conds = {}
        for key, value in kwargs.items():
            if value is None:
                raise Exception("value cannot be None")

            if isinstance(value, (set, list, tuple)):
                conds[key] = CondField.create(*value)
            elif isinstance(value, dict):
                conds[key] = CondField.create(**value)
            elif isinstance(value, CondField):
                conds[key] = value
            else:
                conds[key] = CondField.create(value)

        for cond in conds:
            cond : CondField
            if not cond.match():
                return False
            
        return True

