import dataclasses
from types import MappingProxyType
from typing import FrozenSet
from umodel.attrs import U_ValidationError
from umodel.ustats import UTrackerStats
from umodel.cond import CondField, CondLex
import inspect 
import logging

class UTracker(type):
    _analyzed : dict= {}
    _instances : dict = {}

    def __call__(cls, *args, **kwargs):
        """
        constructor method
        """
        # sep to avoid name conflict for different cls
        stats = cls.get_stats()

        # get primary key
        primary_key = stats.primary_key
        # get primary key value
        primary_key_value = kwargs.get(primary_key, None)
        try:
            primary_key_value = str(primary_key_value)
        except:
            raise U_ValidationError(f"primary key value must be castable to str")

        if primary_key_value is None:
            raise ValueError("primary key value is None")
        # check if primary key value is unique
        if primary_key_value in cls._instances[cls]:
            raise U_ValidationError("cannot instantiate with duplicate primary key value")
        instance = super().__call__(*args, **kwargs)
        cls._instances[cls][primary_key_value] = instance
        return instance

    def __contains__(cls, item):
        if item.__class__ not in cls._instances:
            return False
        if not hasattr(item, 'primary_key'):
            return False

        return str(item.primary_key) in cls._instances[item.__class__]

    def yield_instance(cls, reverse : bool = False,**kwargs):
        if cls not in cls._instances:
            return

        instances : dict = cls._instances[cls]
        
        if len(kwargs) == 0:
            for key, val in instances.items():
                yield key, val
            return 

        condlex = CondLex(**kwargs)

        for key, val in instances.items():
            datadict = dataclasses.asdict(val)
            if condlex.match(**datadict) != reverse:
                yield key, val

    def yield_field(cls, fieldname : str, yield_all : bool = False, reverse : bool = False, **kwargs):
        stats : UTrackerStats = cls.get_stats()
        if fieldname not in stats.all_fields:
            return

        for key, val in cls.yield_instance(reverse, **kwargs):
            attr = getattr(val, fieldname, None)
            if attr is None:
                continue
            if yield_all:
                yield attr, key, val
            else:
                yield attr
        

    def yield_keys(cls, reverse : bool = False, **kwargs):
        for key, val in cls.yield_instance(reverse, **kwargs):
            yield key

    def get_stats(cls) -> UTrackerStats:
        if cls not in cls._instances:
            cls._instances[cls] = {}

        if cls not in cls._analyzed:
            cls._analyzed[cls] = UTrackerStats.analyze_uitem(cls)

        return cls._analyzed[cls]

    def remove(cls, reverse : bool = False,**kwargs):
        if cls not in cls._instances:
            return
        instances  = cls._instances[cls].keys()

        frozekeys = frozenset(instances)
        for key in frozekeys:
            condlex = CondLex(**kwargs)
            datadict = dataclasses.asdict(cls._instances[cls][key])
            if condlex.match(**datadict) != reverse:
                del cls._instances[cls][key]
    
    def remove_this(cls, item):
        if cls not in cls._instances:
            return
    
        if item.__class__ not in cls._instances:
            return

        # get primary key
        # get primary key
        cls._instances[cls].pop(str(item.primary_key), None)
        del item
    
    def check_unique(cls, key : str, value, ignore_this = None, ignore_none : bool = True, reverse : bool = False,**kwargs):
        stats = cls.get_stats()
        if not stats.is_unique_key(key):
            return None

        if value is None and ignore_none:
            return True

        for attr, kkey, kval in cls.yield_field(key,yield_all=True,reverse=reverse, **kwargs):
            if attr is None and ignore_none:
                continue
            if ignore_this == kkey:
                continue
            if attr == value:
                return False

        return True

    def check_iterable_unique(cls, key : str, value, ignore_this = None, ignore_none : bool = True, reverse : bool = False, **kwargs):
        stats = cls.get_stats()

        if not stats.is_iterable_unique_key(key):
            return None

        if value is None and ignore_none:
            return True

        unique = set()
        for attr, kkey, kval in cls.yield_field(key,yield_all=True,reverse=reverse, **kwargs):
            if attr is None and ignore_none:
                continue
            if ignore_this == kkey:
                continue
            unique.update(attr)

        if value in unique:
            return False

        return True

    def check_callables(cls, name, val, primary_key, item):
        if val is None:
            return val

        stats = cls.get_stats()

        for func in stats.yield_callables(name):
            # check func parameters needed
            func_parameters = inspect.signature(func).parameters
            try:
                if len(func_parameters) == 1:
                    res = func(val)
                else:
                    func_kwargs ={
                        "name": name,
                        "val": val,
                        "primary_key": primary_key,
                        "tracker": cls,
                        "item" : item,
                        "stats" : stats,
                    }

                    func_kwargs = {k:v for k,v in func_kwargs.items() if k in func_parameters}
                    res = func(**func_kwargs)
            except Exception as e:
                logging.error(f"{func.__name__} failed with {e}")
                raise U_ValidationError(f"{name} is not valid ({val})")

            if isinstance(res, bool) and res == False:
                raise U_ValidationError(f"{name} is not valid ({val}) [failed func {func.__name__}]")
            elif isinstance(res, bool):
                continue
            elif res is None:
                continue
            else:
                val = res

            if val is None:
                raise U_ValidationError(f"{name} is None caused by func {func.__name__}")

        return val