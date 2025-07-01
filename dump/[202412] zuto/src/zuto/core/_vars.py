
import os
import typing

class CtxVars:
    def __getitem__(self, key : str) -> typing.Any:
        return os.environ[key]
    
    def __setitem__(self, key : str, value : typing.Any):
        os.environ[key] = value
