
from dataclasses import dataclass
import typing


@dataclass
class ValuePair:
    """
    A class to represent a single key-value pair.
    """

    value : typing.Any
    type_ : str = None

    @classmethod
    def body(cls, value):
        return cls(value, 'body')

    @classmethod
    def param(cls, value):
        return cls(value, 'param')
    
    @classmethod
    def path(cls, value):
        return cls(value, 'path')
    
    @classmethod
    def header(cls, value):
        return cls(value, 'header')

    @classmethod
    def cookie(cls, value):
        return cls(value, 'cookie')


class ValueGroup:
    """
    A class to represent a group of key-value pairs, basically a dict with a type_ attribute.
    """

    def __init__(self, type_ : str = None, **kwargs) -> None:
        self.kwargs = kwargs
        self.type_ = type_

    @classmethod
    def body(cls, **kwargs):
        return cls('body', **kwargs)

    @classmethod
    def param(cls, **kwargs):
        return cls('param', **kwargs)

    @classmethod
    def path(cls, **kwargs):
        return cls('path', **kwargs)

    @classmethod
    def header(cls, **kwargs):
        return cls('header', **kwargs)

    @classmethod
    def cookie(cls, **kwargs):
        return cls('cookie', **kwargs)


class ExportArg(ValuePair):
    """
    A class to represent a single key-value pair to be passed to the export model.
    """

    def __init__(self, value : typing.Any, key : str) -> None:
        super().__init__(value, 'additional')
        self.key = key
