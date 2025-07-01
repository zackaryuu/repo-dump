from pydantic import BaseModel
from habilBase.requestMap.base import get_api_status
from habilBase.reqHandler import DEFAULT_HANDLER
from utils.testcase import testcase_template

from habilBase.requestMap.user import login

class t_requestmap_base(testcase_template):

    def test_api_up(self):
        class Status(BaseModel):
            status : bool
        
        c = DEFAULT_HANDLER(get_api_status,
            export = Status,
            export_from_parsed=True
        )
        self.assertTrue(c.obj.status)
        pass

    def test_login_poc(self):
        class Login(BaseModel):
            id : str
            apiToken : str
            username : str
        
        c = login(
            username="prozacmail@gmail.com",
            password="`1qazxsw2",
            export=Login,
            export_from_data=True
        )
        pass