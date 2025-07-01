
from functools import cached_property
import typing
from pydantic import BaseModel

class ZutoPart(BaseModel):
    model_config = {
        "ignored_types" : (cached_property, )
    }

    __block_auto__ = False

    @cached_property
    def _is_part_fields(self) -> typing.Dict[str, int]:
        results = {}
        for field in self.model_fields.keys():
            val = getattr(self, field, None)
            if val is None:
                continue
            if isinstance(val, ZutoPart):
                results[field] = 0 if not val.__block_auto__ else -1
            elif isinstance(val, list) and any(isinstance(item, ZutoPart) for item in val):
                results[field] = 1 if not any(item.__block_auto__ for item in val) else -1
            elif isinstance(val, dict) and any(isinstance(item, ZutoPart) for item in val.values()):
                results[field] = 2 if not any(item.__block_auto__ for item in val.values()) else -1
        return results

    def _on_execute(self, ctx, blocking : int = -1):
        if blocking == 0:
            return
        tb = -1 if blocking == -1 else blocking - 1
        for field, level in self._is_part_fields.items():
            val = getattr(self, field, None)
            if val is None:
                continue
            if level == 0:
                val._on_execute(ctx, tb)
            elif level == 1:
                for item in val:
                    item._on_execute(ctx, tb)
            elif level == 2:
                for item in val.values():
                    item._on_execute(ctx, tb)

    def _execute_child(self, name : str, ctx, blocking : int = 1):
        val = getattr(self, name, None)
        if val is None:
            return 1
        assert name in self._is_part_fields, f"Field {name} not found"
        tb = -1 if blocking == -1 else blocking - 1
        if isinstance(val, ZutoPart):
            res = val._on_execute(ctx, tb)
        elif isinstance(val, list) and any(isinstance(item, ZutoPart) for item in val):
            for item in val:
                res = item._on_execute(ctx, tb) or res
        elif isinstance(val, dict) and any(isinstance(item, ZutoPart) for item in val.values()):
            for item in val.values():
                res = item._on_execute(ctx, tb) or res
        return res
    


