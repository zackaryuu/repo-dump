import typing
from habil.base.clientInterface import HabilClientInterface

class AbcHandler:
    def __init__(self, client : HabilClientInterface) -> None:
        self.client = client
    
    @typing.overload
    def get(self, id : typing.Union[str, int]) -> typing.Any:
        pass
    
    @typing.overload
    def get(self, name: str) -> typing.Any:
        pass
    
    def get(self, key : typing.Union[int, str]) -> typing.Any:
        raise NotImplementedError
    
    def create(self, **data) -> typing.Any:
        raise NotImplementedError
    
    def delete(self, key : typing.Union[int, str]) -> typing.Any:
        raise NotImplementedError
    
    def edit(self, obj : typing.Any, **data) -> typing.Any:
        raise NotImplementedError
    
    def getAll(self) -> typing.Any:
        raise NotImplementedError
    