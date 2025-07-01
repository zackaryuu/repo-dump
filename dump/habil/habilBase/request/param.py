from pydantic import BaseModel, Field
import typing

class RequestParam(BaseModel):
    name : str
    value : typing.Any
    type_ : typing.Literal["path", "param", "header", "body", "cookie"]

    @classmethod
    def path(cls, name : str, value : typing.Any, alias : typing.Optional[str] = None):
        return cls(name=name, value=value, type_="path", alias=alias)

    @classmethod
    def param(cls, name : str, value : typing.Any, alias : typing.Optional[str] = None):
        return cls(name=name, value=value, type_="param", alias=alias)
    
    @classmethod
    def header(cls, name : str, value : typing.Any, alias : typing.Optional[str] = None):
        return cls(name=name, value=value, type_="header", alias=alias)
    
    @classmethod
    def body(cls, name : str, value : typing.Any, alias : typing.Optional[str] = None):
        return cls(name=name, value=value, type_="body", alias=alias)
    
    @classmethod
    def cookie(cls, name : str, value : typing.Any, alias : typing.Optional[str] = None):
        return cls(name=name, value=value, type_="cookie", alias=alias)

