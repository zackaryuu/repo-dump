
from string import Formatter
import typing
from pydantic import BaseModel, validator, Field
from habilBase.request.actionPair import PostProcessPair
from habilBase.request.auth import AuthInterface
from habilBase.request.requestPacker import RequestPacker
from habilBase.request.requester import RequesterResponse
from habilBase.request.specifier import RequestParamSpecifier
import requests

from habilBase.request.valuePair import ExportArg, ValueGroup, ValuePair

class RequestBase:
    def __init__(self, base_url : str) -> None:
        if not isinstance(base_url, str):
            raise ValueError(f'Url must be a string, not {type(base_url)}')

        # if not prefixed with http:// or https://
        base_url = "https://" + base_url if not base_url.startswith("http") else base_url
        
        # if not suffixed with /
        base_url = base_url + "/" if not base_url.endswith("/") else base_url        
        
        self.base_url = base_url
        
    def create(self, 
        url : str, 
        *args,
        method : typing.Union[
            typing.Literal['get', 'post', 'put', 'delete', 'patch', 'options'],
            typing.Callable
        ] =  "get", 
        export_model : BaseModel = None,
        require_auth : bool = True,           
    ):
        if url.startswith("/"):
            url = url[1:]
        
        return RequestCase.create(
            self.base_url + url,
            *args,
            method=method,
            export_model=export_model,
            require_auth=require_auth,
        )
    
        

class RequestCase(BaseModel):
    class Config:
        arbitrary_types_allowed = True
        frozen=True
        orm_mode = True

    url : str
    method : typing.Union[str, typing.Callable]
    mapper : typing.List[RequestParamSpecifier] = Field(default_factory=list)
    postprocess_pairs : typing.List[PostProcessPair] = Field(default_factory=list)
    export_model : typing.Optional[type] = None
    require_auth : bool = False

    # 
    unique_key_mappings : typing.Dict[str, str] = Field(default_factory=dict)
    
    @validator('mapper', pre=True)
    def mapper_validator(cls, v):
        if not isinstance(v, list):
            raise ValueError(f'Mapper must be a list, not {type(v)}')
        
        v: typing.List[RequestParamSpecifier]

        # checks if all of them are unique
        unique_checker = set([(x.name, x.type_) for x in v])
        if len(unique_checker) != len(v):
            raise ValueError('Mapper items must be unique')

        return v
    
    @validator('method', pre=True)  
    def method_validator(cls, v):
        if isinstance(v, str):
            v = v.lower()
            match v:
                case 'get':
                    return requests.get
                case 'post':
                    return requests.post
                case 'put':
                    return requests.put
                case 'delete':
                    return requests.delete
                case 'patch':
                    return requests.patch
                case 'options':
                    return requests.options
                case _:
                    raise ValueError(f'Unknown method {v}')
        elif isinstance(v, typing.Callable):
            return v
        else:
            raise ValueError(f'Unknown method {v}')    

    def __init__(self, **data) -> None:
        super().__init__(**data)
        # process unique key mappings
        for item in self.mapper:
            if item.name not in self.unique_key_mappings:
                self.unique_key_mappings[item.name] = item.type_
                continue
            
            self.unique_key_mappings.pop(item.name)
        
    
    @classmethod
    def create(cls, 
        url : str, 
        *args,
        method : typing.Union[
            typing.Literal['get', 'post', 'put', 'delete', 'patch', 'options'],
            typing.Callable
        ] =  "get", 
        export_model : BaseModel = None,
        require_auth : bool = True,
    ):
        url_vars = [i[1] for i in Formatter().parse(url) if i[1] is not None]
        specifiers = []
        postprocess_pairs = []
        for var in url_vars:
            specifiers.append(RequestParamSpecifier.PATH(name=var, required=True, cast_type=str))
        
        for arg in args:
            if isinstance(arg, RequestParamSpecifier):
                specifiers.append(arg)
            elif isinstance(arg, PostProcessPair):
                postprocess_pairs.append(arg)
            else:
                raise ValueError(f'Unknown argument {arg}')

        return cls(
            url = url,
            method = method,
            mapper = specifiers,
            export_model = export_model,
            postprocess_pairs = postprocess_pairs,
            require_auth = require_auth
        )

    def make_request(
        self,
        *args,
        export : BaseModel = None,
        export_from_parsed : bool = False,
        export_from_data : bool =True,
        **kwargs
    ):
        export_additional_args : dict = {},

        packer = RequestPacker.create_from_requestCase(self)
        post_process_pairs = self.postprocess_pairs.copy()

        export_model = export if export else self.export_model

        auth : AuthInterface = None

        for arg in args:
            # add ability to parse auth interface
            if isinstance(arg, AuthInterface):
                if auth is not None:
                    raise ValueError('Auth interface already set')
                auth = arg
                
            if isinstance(arg, ValueGroup):
                for k, v in arg.kwargs.items():
                    packer[arg.type_, k] = v
            if isinstance(arg, PostProcessPair):
                post_process_pairs.append(arg)

        # if auth required
        if self.require_auth and auth is None:
            raise ValueError('Auth interface required')

        for k, v in kwargs.items():
            if k in self.unique_key_mappings: 
                packer[self.unique_key_mappings[k], k] = v
            elif isinstance(v, dict):
                for k2, v2 in v.items():
                    packer[k, k2] = v2
            elif isinstance(v, ExportArg):
                export_additional_args[k] = v
            elif isinstance(v, ValuePair):
                packer[v.type_, k] = v.value

        return RequesterResponse.request(
            method=self.method,
            postprocessors=post_process_pairs,
            export=export_model,
            export_from_parsed=export_from_parsed,
            export_from_data=export_from_data,
            kwargs=packer.create_request_kwargs(),
            export_additional_args=export_additional_args,
            auth = auth
        )

    def __call__(
        self,
        *args,
        export : BaseModel = None,
        export_from_parsed : bool = False,
        export_from_data : bool =True,
        **kwargs
    ):
        return self.make_request(
            *args,
            export=export,
            export_from_parsed=export_from_parsed,
            export_from_data=export_from_data,
            **kwargs
        )

    
        
        
