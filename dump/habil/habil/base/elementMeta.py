from datetime import datetime
import typing
import uuid
from pydantic import BaseModel, Field
from pydantic.main import ModelMetaclass

class HabilElementMeta(ModelMetaclass):
    
    _instances = {}

    def __call__(cls, *args, **kwargs):
        id = kwargs.get("id", None)
        if id is None and len(args) ==1 and isinstance(args[0], str):
            id = args[0]

        if not isinstance(id, uuid.UUID):
            id = uuid.UUID(id)
            kwargs["id"] = id
            
        # extract special flags
        nocache = kwargs.pop("__no_cache", False)
        if nocache:
            return super().__call__(*args, **kwargs)

        noupdate = kwargs.pop("__no_update", False)

        if cls not in cls._instances:
            cls._instances[cls] = {}

        if id not in cls._instances[cls]:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls][id] = instance
            return instance

        instance = cls._instances[cls][id]
        if not noupdate:
            instance._update(**kwargs)
        return instance
