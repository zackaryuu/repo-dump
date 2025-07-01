import uuid
from dataclasses import dataclass, field
import typing
import yaml

@dataclass
class Meta:
    cond : str = None
    lifetime : int = None
    cleanup : bool = False
        
@dataclass(slots=True)
class Task:
    name  : str
    meta : Meta = field(default_factory=Meta)
    steps : typing.List[typing.Union[dict, str]] = field(default_factory=list)
    description : str = None
    id : str = None
    tags : typing.List[str] = field(default_factory=list)

    @staticmethod
    def from_yaml(path : str):
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            meta = Meta(**data.pop("meta", {}))
            return Task(**data, meta=meta)
        
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        
