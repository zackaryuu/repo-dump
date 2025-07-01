import typing
import uuid
from pydantic import BaseModel, Field
from habil.base.elementMeta import HabilElementMeta
from habil.base.clientMeta import HabilClientMeta
from habil.base.clientInterface import HabilClientInterface
from datetime import datetime

from habilBase.request.auth import AuthInterface

class HabilElement(BaseModel, frozen=True, metaclass=HabilElementMeta):
    _client_id : uuid.UUID
    id : typing.Union[uuid.UUID, str]
    name : str
    last_updated : datetime = Field(default_factory=datetime.now)
    init_timestamp : datetime = Field(default_factory=datetime.now)

    def _update(self, **data):
        data.pop("last_updated", None)
        data["init_timestamp"] = self.init_timestamp
        ins = self.__class__(**data, __no_cache=True)
        self.__dict__.update(ins.__dict__)

    def update(self):
        """
        pulls the latest data from the server and updates the object
        """
        raise NotImplementedError

class HabilClient(HabilClientInterface, BaseModel, AuthInterface,metaclass=HabilClientMeta):
    user_id : typing.Union[uuid.UUID, int, str]
    api_token : str
    app_id : typing.Optional[str]

    def __init__(self, **data):
        super().__init__(**data)
        self._client_id = uuid.uuid4()
    
    @property
    def headers(self) -> dict:
        return {
            "x-api-user": self.user_id,
            "x-api-key": self.api_token,
            "x-client" : self.app_id if self.app_id else self.user_id
        }

    def unpack(self, data: dict):
        if data.get("headers") is None:
            data["headers"] = {}

        data["headers"].update(
            self.headers
        )