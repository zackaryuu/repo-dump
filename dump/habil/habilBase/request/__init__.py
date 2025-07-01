from habilBase.request.specifier import RequestParamSpecifier as _RequestParamSpecifier
from habilBase.request.case import RequestBase as _RequestBase

REQUEST_BASE = _RequestBase

BODY = _RequestParamSpecifier.BODY
PARAM = _RequestParamSpecifier.PARAM
PATH = _RequestParamSpecifier.PATH
HEADER = _RequestParamSpecifier.HEADER
COOKIE = _RequestParamSpecifier.COOKIE

from habilBase.request.valuePair import ValueGroup as _ValueGroup

bodyGroup = _ValueGroup.body
paramGroup = _ValueGroup.param
pathGroup = _ValueGroup.path
headerGroup = _ValueGroup.header
cookieGroup = _ValueGroup.cookie

from habilBase.request.valuePair import ValuePair as _ValuePair

body = _ValuePair.body
param = _ValuePair.param
path = _ValuePair.path
header = _ValuePair.header
cookie = _ValuePair.cookie

from habilBase.request.actionPair import ResParsePair as RES_PARSE
from habilBase.request.valuePair import ExportArg as EXPORT_ARG

import habilBase.request.__init_structs__ as models

