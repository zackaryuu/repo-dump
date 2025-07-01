from pydantic.main import ModelMetaclass

class HabilClientMeta(ModelMetaclass):
    _clients : dict = {}
    
    def __call__(cls, *args, **kwargs):
        id = kwargs.get("id", None)
        
        if id is None:
            raise ValueError("Client id is required")
        
        if id not in cls._clients:
            instance = super().__call__(*args, **kwargs)
            cls._clients[id] = instance
            return instance
        
        return cls._clients[id]
    
    
    def getClient(id : str):
        return HabilClientMeta._clients[id]
    
