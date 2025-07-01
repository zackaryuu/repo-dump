import orjson
from ..io import *  # noqa


def load_json(path: str, **kwargs):
    openKwargs = kwargs.pop("open", {})
    loadKwargs = kwargs.pop("load", {})
    with open(path, "rb", **openKwargs) as f:
        return orjson.loads(f.read(), **loadKwargs, **kwargs)


def dump_json(obj, path: str, **kwargs):
    openKwargs = kwargs.pop("open", {})
    dumpKwargs = kwargs.pop("dump", {})
    with open(path, "wb", **openKwargs) as f:
        return orjson.dumps(obj, f, **dumpKwargs, **kwargs)


def loads_json(s: str, **kwargs):
    return orjson.loads(s, **kwargs)


def dumps_json(obj, **kwargs):
    return orjson.dumps(obj, **kwargs)


def load_json_w_encoding(path: str, **kwargs):
    openKwargs = kwargs.pop("open", {})
    openKwargs["encoding"] = kwargs.pop("encoding", "utf-8")
    loadKwargs = kwargs.pop("load", {})
    with open(path, "rb", **openKwargs) as f:
        return orjson.loads(f.read(), **loadKwargs, **kwargs)


def dump_json_w_encoding(obj, path: str, **kwargs):
    openKwargs = kwargs.pop("open", {})
    openKwargs["encoding"] = kwargs.pop("encoding", "utf-8")
    dumpKwargs = kwargs.pop("dump", {})
    with open(path, "wb", **openKwargs) as f:
        return orjson.dumps(obj, **dumpKwargs, **kwargs)


# Override the default loaders/dumpers
DEFAULT_LOAD[0][1] = load_json
DEFAULT_LOAD[-1][1] = load_json
DEFAULT_DUMP[0][1] = dump_json
DEFAULT_DUMP[-1][1] = dump_json
DEFAULT_LOADS[0][1] = loads_json
DEFAULT_LOADS[1][1] = loads_json

# Override UTF8 variants
UTF8_LOAD[0][1] = load_json_w_encoding
UTF8_DUMP[0][1] = dump_json_w_encoding
