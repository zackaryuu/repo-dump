from habil.handler.abcHandler import AbcHandler
import typing
import habilBase.requestMap.tag as mapping
from habilBase.reqHandler import DEFAULT_HANDLER

class TagsHandler(AbcHandler):
    def getAll(self) -> typing.Any:
        res = DEFAULT_HANDLER(
            mapping.get_a_users_tags,
            self.client
        )
        pass