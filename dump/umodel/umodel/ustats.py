import dataclasses
from dataclasses import dataclass
from pprint import pprint
import typing
from umodel.attrs import ALL_UKEYS, U_ValidationError, UIterableUniqueKey, UKey, UPrimaryKey, UniqueKey
import types
import inspect


@dataclass(frozen=True)
class UTrackerStats:
    all_fields : typing.List[str] = dataclasses.field(default_factory=list)
    primary_key : str = None
    """
    standard unique key = None
    iterable unique key = subtype
    """
    unique_keys : dict = dataclasses.field(default_factory=dict)
    callables : typing.Dict[str, typing.Callable] = dataclasses.field(default_factory=dict)
    atomic_types : typing.Dict[str, type] = dataclasses.field(default_factory=dict)

    @classmethod
    def analyze_uitem(cls, uitem_cls: type) -> 'UTrackerStats':
        # if not dataclass
        if not dataclasses.is_dataclass(uitem_cls):
            raise Exception("Not a dataclass")

        dataclass_fields = dataclasses.fields(uitem_cls)

        primary_key = None
        all_fields = []
        atomic_types = {}
        unique_keys = {}
        callables = {}

        for field in dataclass_fields:
            # all fields
            field : dataclasses.Field
            all_fields.append(field.name)

            #if field type is not typing.union
            if field.type== typing.Union:
                ukeys = [ukeys]
            ukeys = typing.get_args(field.type)
            
            # parse conds
            is_primarykey = UPrimaryKey in ukeys 
            is_uniquekey = UniqueKey in ukeys
            is_iterable_uniquekey = UIterableUniqueKey in ukeys

            # count occurrences of all ukeys
            count = 0
            for ukey in ukeys:
                if ukey in ALL_UKEYS:
                    count += 1
            
                if count > 1:
                    raise U_ValidationError(f"Field {field.name} has more than one UKEY")

                if ukey in (int, bool, str, float, complex, bytes, list, tuple, set, frozenset):
                    atomic_types[field.name] = ukey

                field_origin = typing.get_origin(ukey)
                if field_origin is None:
                    continue
                
                atomic_types[field.name] = field_origin
                
                if is_iterable_uniquekey and (subtype := typing.get_args(ukey)) is not None:
                    unique_keys[field.name] = subtype[0]

            # get all callables
            field_callables = set([x for x in ukeys if inspect.isfunction(x)])
            if len(field_callables) != 0:
                callables.update({field.name : list(field_callables)})
            
            # primary key
            if is_primarykey and primary_key is not None:
                raise Exception("Multiple primary keys")
            elif is_primarykey:
                primary_key = field.name

            # unique keys
            if is_uniquekey:
                unique_keys[field.name] = None

        stats = UTrackerStats(
            all_fields=all_fields,
            primary_key=primary_key,
            unique_keys=unique_keys,
            callables=callables,
            atomic_types=atomic_types
        )

        return stats

    def is_field(self, field_name: str) -> bool:
        return field_name in self.all_fields

    def is_primary_key(self, field_name: str) -> bool:
        return field_name == self.primary_key

    def is_unique_key(self, field_name: str) -> bool:
        return field_name in self.unique_keys

    def is_iterable_unique_key(self, field_name: str) -> bool:
        return field_name in self.unique_keys and self.unique_keys[field_name] is not None

    def get_atomic_type(self, field_name: str) -> type:
        return self.atomic_types.get(field_name, None)

    def yield_callables(self, field_name: str) -> typing.List[typing.Callable]:
        if field_name not in self.callables:
            return
        for func in self.callables[field_name]:
            yield func

    def set_cast(self, field_name : str, val) -> typing.Any:
        if val == None:
            return None

        if field_name not in self.atomic_types:
            return val

        cast = self.atomic_types[field_name](val)

        if isinstance(cast, (list, tuple, set, frozenset)) and self.is_iterable_unique_key(field_name):
            for i, item in enumerate(cast):
                cast[i] = self.unique_keys[field_name](item)

        return cast
            
        
        