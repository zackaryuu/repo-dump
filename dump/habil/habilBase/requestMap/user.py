from habilBase.request import RES_PARSE, BODY, PARAM, PATH, HEADER, COOKIE
from habilBase.requestMap import CASE

login = CASE(
    "user/auth/local/login",
    BODY(name="username", required=True),
    BODY(name="password", required=True),
    method="POST",
    require_auth=False,
)