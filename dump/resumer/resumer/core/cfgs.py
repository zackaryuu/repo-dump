
import typing
from typing_extensions import TypedDict


class RuntimeConfig(TypedDict):
    bkup_temp_dir : typing.Optional[str]

    debug : typing.Optional[bool]

    copyback_log : typing.Optional[bool]