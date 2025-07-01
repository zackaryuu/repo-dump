
import typing
from pydantic import BaseModel, Field
from habilBase.request.specifier import RequestParamSpecifier

class RequestPacker(BaseModel, frozen=True):
    url : str
    params : typing.Dict[RequestParamSpecifier, typing.Any] = Field(default_factory=dict)
    headers : typing.Dict[RequestParamSpecifier, typing.Any] = Field(default_factory=dict)
    cookies : typing.Dict[RequestParamSpecifier, typing.Any] = Field(default_factory=dict)
    body : typing.Dict[RequestParamSpecifier, typing.Any] = Field(default_factory=dict)
    path : typing.Dict[RequestParamSpecifier, typing.Any] = Field(default_factory=dict)

    @classmethod
    def create_from_requestCase(cls, requestCase):
        params = {}
        headers = {}
        cookies = {}
        body = {}
        path = {}
        for specifier in requestCase.mapper:
            if specifier.type_ == 'param':
                params[specifier] = None
            elif specifier.type_ == 'header':
                headers[specifier] = None
            elif specifier.type_ == 'cookie':
                cookies[specifier] = None
            elif specifier.type_ == 'body':
                body[specifier] = None
            elif specifier.type_ == 'path':
                path[specifier] = None

        return cls(
            url = requestCase.url,
            params = params,
            headers = headers,
            cookies = cookies,
            body = body,
            path = path
        )

    def __getitem__(self, *args):
        if not len(args) == 2:
            raise ValueError('RequestPacker.__getitem__ only accepts two arguments')
        specifier, key = args
        if not isinstance(specifier, str) and not isinstance(key, str):
            raise ValueError('RequestPacker.__getitem__ only accepts two string arguments')
        match specifier:
            case 'param':
                return self.params[key]
            case 'header':
                return self.headers[key]
            case 'cookie':
                return self.cookies[key]
            case 'body':
                return self.body[key]
            case 'path':
                return self.path[key]

        raise ValueError(f'Unknown specifier {specifier}')


    def __setitem__(self, key, value):
        if not isinstance(key, typing.Iterable):
            raise ValueError('RequestPacker.__setitem__ only accepts two (or max 3) arguments')

        allow_adding_new = False
        if len(key) == 3 and isinstance(key[2], bool):
            allow_adding_new = key[2]

        specifier, key = key
        specifier = specifier.lower()
        if specifier.endswith('s'):
            specifier = specifier[:-1]
        target = None
        match specifier:
            case 'param':
                target = self.params
            case 'header':
                target = self.headers
            case 'cookie':
                target = self.cookies
            case 'body':
                target = self.body
            case 'path':
                target = self.path

        if target is None:
            raise ValueError(f'Unknown specifier {specifier}')

        for specifier in target:
            if specifier.name == key:
                target[specifier] = value
                return

        if allow_adding_new:
            target[key] = value
            return

        raise ValueError(f'Unknown key {key}')
    
    def _create_validated_dict(self, target : typing.Dict[RequestParamSpecifier, typing.Any]):
        result = {}
        for specifier, value in target.items():
            val = specifier.get(value)
            if val is None:
                continue
            result[specifier.name] = val
        if len(result) == 0:
            return None
    
        return result

    def create_request_kwargs(self):
        kwargs = {
            'params' : self._create_validated_dict(self.params),
            'headers' : self._create_validated_dict(self.headers),
            'cookies' : self._create_validated_dict(self.cookies),
            'json' : self._create_validated_dict(self.body),
        }

        
        path = self._create_validated_dict(self.path)
        path = path if path else {}
        new_url = self.url.format(**path)
        kwargs['url'] = new_url

        return kwargs
