from habilBase.request import RES_PARSE, BODY, PARAM, PATH, HEADER, COOKIE
from habilBase.requestMap import CASE

get_api_status = CASE(
    "status",
    RES_PARSE("status", lambda x: x == "up"),
    require_auth=False
)