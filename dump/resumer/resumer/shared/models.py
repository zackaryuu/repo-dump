import typing
from typing_extensions import TypedDict

class Experience(TypedDict):
    position : str
    positionType : typing.Optional[
        typing.Literal["full time", "part time", "contract", "intern", "volunteer"]
    ]
    organization : str
    startDate : str
    endDate : typing.Optional[str]
    location : str
    items : typing.List[str]

class Education(TypedDict):
    degree : str
    school : str
    startDate : str
    endDate : typing.Optional[str]
    location : str
    items : typing.List[str]

class Project(TypedDict):
    position : str
    name : str
    startDate : str
    endDate : typing.Optional[str]
    type : str
    items : typing.List[str]