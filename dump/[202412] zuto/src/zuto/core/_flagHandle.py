import typing

class CtxFlagHandle:
    def __init__(self):
        self.__flags = set()

    @property
    def current(self) -> typing.Set[str]:
        return set(self.__flags)
    
    @property
    def _inner(self) -> typing.Set[str]:
        return self.__flags
    
    def set(self, *flags):
        for flag in flags:
            self.__flags.add(flag)

    def has(self, flag : str) -> bool:
        return flag in self.__flags
    
    def clear(self):
        self.__flags.clear()

    
    
