
import typing

class CtxMeta:
    def __init__(self):
        self.__currentStack = [{}]

    @property
    def current(self) -> typing.Dict[str, typing.Any]:
        return self.__currentStack[-1]

    def push(self, key : str = None, **kwargs):
        if key:
            if key not in self.current:
                self.current[key] = {}
            new = self.current[key]
            self.__currentStack.append(new)
        for key, val in kwargs.items():
            self.current[key] = val

    def pop(self):
        if len(self.__currentStack) > 1:
            self.__currentStack.pop()

    def rebase(self):
        self.__currentStack = [self.__currentStack[0]]

    def __getitem__(self, *keys : typing.Tuple[str, ...]) -> typing.Any:
        target = self.__currentStack[0]
        if len(keys) == 1 and "/" in keys[0]:
            keys = keys[0].split("/")
        for key in keys:
            target = target[key]
        return target
    
    def __setitem__(self, *keys : typing.Tuple[str, ...], value : typing.Any):
        target = self.__currentStack[0]
        if len(keys) == 1 and "/" in keys[0]:
            keys = keys[0].split("/")
        for key in keys[:-1]:
            if key not in target:
                target[key] = {}
            target = target[key]
        target[keys[-1]] = value


