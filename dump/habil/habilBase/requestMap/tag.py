from habilBase.request import RES_PARSE, BODY, PARAM, PATH, HEADER, COOKIE
from habilBase.requestMap import CASE

create_a_new_tag = CASE(
    "tags",
    BODY(name="name", required=True),
    RES_PARSE("name"),
    RES_PARSE("id"),
    method="POST",
)

delete_a_user_tag = CASE(
    "tags/{tagId}",
    method="DELETE",
)

get_a_tag = CASE(
    "tags/{tagId}",
)

get_a_users_tags = CASE(
    "tags",
)
 
reorder_a_tag = CASE(
    "reorder-tags",
    BODY(name="tagId", required=True),
    BODY(name="to", cast_type=int, required=True),
)

update_a_tag = CASE(
    "tags/{tagId}",
    BODY(name="name", required=True),
)

