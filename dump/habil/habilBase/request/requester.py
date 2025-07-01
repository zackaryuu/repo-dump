import typing
from pydantic import BaseModel, Field
from pydantic.main import ModelMetaclass
import requests

from habilBase.request.actionPair import PostProcessPair
from habilBase.request.auth import AuthInterface

class RequesterResponseMeta(ModelMetaclass):
    pass


class RequesterResponse(BaseModel, metaclass=RequesterResponseMeta):
    obj : typing.Optional[BaseModel]
    res : requests.Response
    jsondata : typing.Any = None
    parsed : typing.Dict[str, typing.Any] = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True
        frozen=True
        orm_mode = True

    @classmethod
    def request(
        cls, 
        method : typing.Callable, 
        postprocessors : typing.List[PostProcessPair],
        kwargs : dict,
        export : BaseModel =None ,
        export_from_parsed : bool =False,
        export_from_data : bool =True,
        export_additional_args : dict =None,
        auth : AuthInterface = None,  
    ):
        if auth is not None:
            auth.unpack(kwargs)

        response : requests.Response = method(**kwargs)
        
        success_on_json = False
        try:
            data = response.json()
            success_on_json = True
        except:
            data = response.text
        parsed = {}

        modelData = None

        modelAdditionalArgs = {}
        if export_additional_args is not None and isinstance(export_additional_args, dict):
            modelAdditionalArgs = export_additional_args
            

        if success_on_json:
            data_data = data.get('data', {})

            for postprocessor in postprocessors:
                postprocessor(data_data, parsed)

            if export and not export_from_parsed and not export_from_data:
                modelData = export(**data, **modelAdditionalArgs)
            elif export and not export_from_parsed and export_from_data:
                modelData = export(**data_data, **modelAdditionalArgs)
            elif export and export_from_parsed:
                modelData = export(**parsed, **modelAdditionalArgs)
    
        return cls(obj=modelData, res=response, jsondata=data, parsed=parsed)

    @property
    def data(self):
        if not self.jsondata:
            return None

        if "data" in self.jsondata:
            return self.jsondata['data']

        return None

    @property
    def success(self):
        return "success" in self.jsondata and self.jsondata['success']

    @property
    def status(self):
        return self.res.status_code
    


