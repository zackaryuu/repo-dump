# Introduction
this is a lite python wrapper for Habitica API. By `lite` I mean that this wrapper does not implement all the API calls available (but there are base components to facilitate the implementation of new calls). 

# Documentation

## Base Components
### 1. request

* `request` component implements a request call model for generic api calls (currently not available for generic use, it will be available in the future if there is a need for it).

```py

from habilBase.request import (
    CASE,           # case model

    RES_PARSE,      # response parser, this can be used to rename or postprocess data
                    # retrieved from response

    BODY,           # body parameters

    PARAM,          # query parameters

    PATH,           # path parameters

    HEADER,         # header parameters
    
    COOKIE          # cookie parameters
)

```

* a `case` is a request call model for one specific api call. Below is an example call for `login`.
```py

login = CASE(
    "v3/user/auth/local/login",                     # url
    BODY(name="username", required=True),
    BODY(name="password", required=True),
    RES_PARSE("id", rename_to="user_id"),
    RES_PARSE("apiToken", rename_to="api_token"),
    method = "POST"                                 # method
)
```
* A `case` defines the url endpoint, all parameters relevant to the call, and the method type

* `RES_PARSE` is used to rename or postprocess data retrieved from response. In the example above, the response data is parsed to rename `id` to `user_id` and `apiToken` to `api_token`. It is also possible to pass lambda or functions.

* to make the call, simply call the `case` object with the parameters. The following example shows how to make a `get_api_status` call.
```py

get_api_status = CASE(
    "v3/status",
    RES_PARSE("status", lambda x: x == "up")
)

"""
API endpoint returns for example:
{
    "status": "up"
}
"""

case_result = get_api_status()
```

* returned case_result is a `RequesterResponse` class.


### 2. requestMap

* requestMap is the implementation of the request call model for all the api calls. It is a dictionary of `case` objects.