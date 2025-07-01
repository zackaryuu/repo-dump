import typing
from pydantic import BaseModel, Field

class Validator:
    def __init__(self, func : typing.Callable) -> None:
        self.func = func

class RequestParamSpecifier(BaseModel):
    name : str
    default : typing.Optional[typing.Any] = None
    required : bool = False
    cast_type : typing.Optional[typing.Type] = None
    alias : typing.Optional[str] = None
    type_ : typing.Literal["path", "param", "header", "body", "cookie"]
    validators : typing.List[typing.Callable] = Field(default_factory=list)

    def cast(self, value : typing.Any):
        if self.cast_type is None:
            return value

        return self.cast_type(value)

    def __hash__(self):
        return hash(self.name + "|" + self.type_)

    def get(self, value :typing.Any):
        if value is None and self.required and self.default is None:
            raise ValueError(f"Required parameter for {self.name} not provided")

        if value is None and self.default is not None:
            return self.cast(self.default)
        
        for validator in self.validators:
            validator_ret = validator(value)
            if not isinstance(validator_ret, bool):
                value = validator_ret
            
        return self.cast(value)

    def __add__(self, other : typing.Any):
        if isinstance(other, Validator):
            self.validators.append(other.func)
        else:
            raise TypeError(f"Cannot add {type(other)} to {type(self)}")
        return self

    @classmethod
    def BODY(cls, name : str, default : typing.Any = None, required : bool = False, cast_type : typing.Type = None, alias : str = None):
        return cls(name=name, default=default, required=required, cast_type=cast_type, alias=alias, type_="body")

    @classmethod
    def PATH(cls, name : str, default : typing.Any = None, required : bool = False, cast_type : typing.Type = None, alias : str = None):
        return cls(name=name, default=default, required=required, cast_type=cast_type, alias=alias, type_="path")

    @classmethod
    def PARAM(cls, name : str, default : typing.Any = None, required : bool = False, cast_type : typing.Type = None, alias : str = None):
        return cls(name=name, default=default, required=required, cast_type=cast_type, alias=alias, type_="param")

    @classmethod
    def HEADER(cls, name : str, default : typing.Any = None, required : bool = False, cast_type : typing.Type = None, alias : str = None):
        return cls(name=name, default=default, required=required, cast_type=cast_type, alias=alias, type_="header")

    @classmethod
    def COOKIE(cls, name : str, default : typing.Any = None, required : bool = False, cast_type : typing.Type = None, alias : str = None):
        return cls(name=name, default=default, required=required, cast_type=cast_type, alias=alias, type_="cookie")
