from zuu.UTILS.read import read_first_and_last_byte


#  ANCHOR load
def load_json(path: str, **kwargs):
    import json

    openKwargs = kwargs.pop("open", {})
    loadKwargs = kwargs.pop("load", {})
    with open(path, **openKwargs) as f:
        return json.load(f, **loadKwargs, **kwargs)


def load_pickle(path: str, **kwargs):
    import pickle

    openKwargs = kwargs.pop("open", {})
    loadKwargs = kwargs.pop("load", {})
    with open(path, **openKwargs) as f:
        return pickle.load(f, **loadKwargs, **kwargs)


def load_csv(path: str, **kwargs):
    import csv

    openKwargs = kwargs.pop("open", {})
    loadKwargs = kwargs.pop("load", {})
    with open(path, **openKwargs) as f:
        return csv.load(f, **loadKwargs, **kwargs)


def load_txt(path: str, **kwargs):
    openKwargs = kwargs.pop("open", {})
    with open(path, **openKwargs) as f:
        return f.read()


def load_xml(path: str, **kwargs):
    import xml.etree.ElementTree as ET

    openKwargs = kwargs.pop("open", {})
    loadKwargs = kwargs.pop("load", {})
    with open(path, **openKwargs) as f:
        return ET.parse(f, **loadKwargs, **kwargs)


def load_toml(path: str, **kwargs):
    import toml

    return toml.load(path, **kwargs)


def load_yaml(path: str, **kwargs):
    import yaml

    openKwargs = kwargs.pop("open", {})
    loadKwargs = kwargs.pop("load", {})
    with open(path, **openKwargs) as f:
        return yaml.safe_load(f, **loadKwargs, **kwargs)


DEFAULT_LOAD = [
    [lambda path: path.endswith(".json"), load_json],
    [lambda path: path.endswith(".pickle"), load_pickle],
    [lambda path: path.endswith(".csv"), load_csv],
    [lambda path: path.endswith(".txt"), load_txt],
    [lambda path: path.endswith(".toml"), load_toml],
    [lambda path: path.endswith(".xml"), load_xml],
    [
        lambda path: read_first_and_last_byte(path) in [(b"[", b"]"), (b"{", b"}")],
        load_json,
    ],
]


def load(
    path: str,
    _seq: list = DEFAULT_LOAD,
    _throw_error: bool = True,
    _try_all: bool = False,
    **kwargs,
):
    for validator, loader in _seq:
        if validator(path):
            try:
                return loader(path, **kwargs)
            except Exception as e:
                if _try_all:
                    continue
                elif _throw_error:
                    raise e
                else:
                    return None
    raise ValueError(f"No suitable loader found for file: {path}")


# ANCHOR advanced load


def load_json_w_encoding(path: str, **kwargs):
    import json

    openKwargs: dict = kwargs.pop("open", {})
    openKwargs["encoding"] = kwargs.pop("encoding", "utf-8")
    loadKwargs: dict = kwargs.pop("load", {})
    with open(path, **openKwargs) as f:
        return json.load(f, **loadKwargs, **kwargs)


UTF8_LOAD = DEFAULT_LOAD.copy()
UTF8_LOAD[0][1] = load_json_w_encoding


# ANCHOR dump
def dump_json(obj, path: str, **kwargs):
    import json

    openKwargs: dict = kwargs.pop("open", {})
    dumpKwargs: dict = kwargs.pop("dump", {})
    with open(path, "w", **openKwargs) as f:
        json.dump(obj, f, **dumpKwargs, **kwargs)


def dump_pickle(obj, path: str, **kwargs):
    import pickle

    openKwargs: dict = kwargs.pop("open", {})
    dumpKwargs: dict = kwargs.pop("dump", {})
    with open(path, "wb", **openKwargs) as f:
        pickle.dump(obj, f, **dumpKwargs, **kwargs)


def dump_csv(obj, path: str, **kwargs):
    import csv

    openKwargs: dict = kwargs.pop("open", {})
    writeKwargs: dict = kwargs.pop("write", {})
    with open(path, "w", newline="", **openKwargs) as f:
        writer = csv.writer(f, **writeKwargs)
        writer.writerows(obj)


def dump_txt(obj, path: str, **kwargs):
    openKwargs: dict = kwargs.pop("open", {})
    with open(path, "w", **openKwargs) as f:
        f.write(str(obj))


def dump_toml(obj, path: str, **kwargs):
    import toml

    openKwargs: dict = kwargs.pop("open", {})
    dumpKwargs: dict = kwargs.pop("dump", {})
    with open(path, "w", **openKwargs) as f:
        toml.dump(obj, f, **dumpKwargs, **kwargs)


def dump_xml(obj, path: str, **kwargs):
    import xml.etree.ElementTree as ET

    openKwargs: dict = kwargs.pop("open", {})
    dumpKwargs: dict = kwargs.pop("dump", {})
    with open(path, "w", **openKwargs) as f:
        ET.dump(obj, f, **dumpKwargs, **kwargs)


# ANCHOR advanced dump
def dump_json_w_encoding(obj, path: str, **kwargs):
    import json

    openKwargs: dict = kwargs.pop("open", {})
    openKwargs["encoding"] = kwargs.pop("encoding", "utf-8")
    dumpKwargs: dict = kwargs.pop("dump", {})
    dumpKwargs["ensure_ascii"] = kwargs.pop("ensure_ascii", False)
    with open(path, "w", **openKwargs) as f:
        json.dump(obj, f, **dumpKwargs, **kwargs)


DEFAULT_DUMP = [
    [
        lambda path, obj: path.endswith(".json") and isinstance(obj, (dict, list)),
        dump_json,
    ],
    [lambda path, obj: path.endswith(".pickle"), dump_pickle],
    [lambda path, obj: path.endswith(".xml"), dump_xml],
    [lambda path, obj: path.endswith(".csv") and isinstance(obj, list), dump_csv],
    [lambda path, obj: path.endswith(".txt") and isinstance(obj, str), dump_txt],
    [lambda path, obj: path.endswith(".toml") and isinstance(obj, dict), dump_toml],
    [
        lambda path, obj: read_first_and_last_byte(path) in [(b"[", b"]"), (b"{", b"}")]
        and isinstance(obj, (dict, list)),
        dump_json,
    ],
]


def dump(
    obj,
    path: str,
    _seq: list = DEFAULT_DUMP,
    _throw_error: bool = True,
    _try_all: bool = False,
    **kwargs,
):
    for validator, dumper in _seq:
        if validator(path, obj):
            try:
                return dumper(obj, path, **kwargs)
            except Exception as e:
                if not _try_all and _throw_error:
                    raise e
    if _throw_error:
        raise ValueError(f"No suitable dumper found for {path}")


UTF8_DUMP = DEFAULT_DUMP.copy()
UTF8_DUMP[0][1] = dump_json_w_encoding


# ANCHOR loads


def loads_json(s: str, **kwargs):
    import json

    return json.loads(s, **kwargs)


def loads_pickle(s: str, **kwargs):
    import pickle

    return pickle.loads(s, **kwargs)


def loads_csv(s: str, **kwargs):
    import csv

    return csv.loads(s, **kwargs)


def loads_toml(s: str, **kwargs):
    import toml

    return toml.loads(s, **kwargs)


def loads_yaml(s: str, **kwargs):
    import yaml
    from io import StringIO

    return yaml.load(StringIO(s), **kwargs)


def loads_xml(s: str, **kwargs):
    import xml.etree.ElementTree as ET

    return ET.fromstring(s, **kwargs)


DEFAULT_LOADS = [
    [lambda s: s.startswith("{") and s.endswith("}"), loads_json],
    [lambda s: s.startswith("[") and s.endswith("]"), loads_json],
    [lambda s: s.startswith("<") and s.endswith(">"), loads_xml],
    [lambda s: s.startswith(b"\x80") or s.startswith(b"\x00"), loads_pickle],
    [
        lambda s: ((s.startswith("[") and "\n" in s) or "[[" in s) and "=" in s,
        loads_toml,
    ],
    [lambda s: "\t" in s and ";" in s, loads_yaml],
    [lambda s: "," in s and "\n" in s, loads_csv],
]


def loads(
    s: str,
    _seq: list = DEFAULT_LOADS,
    _throw_error: bool = True,
    _try_all: bool = False,
    **kwargs,
):
    for validator, loader in _seq:
        if validator(s):
            try:
                return loader(s, **kwargs)
            except Exception as e:
                if _try_all:
                    continue
                elif _throw_error:
                    raise e
                else:
                    return None
    raise ValueError(f"No suitable loader found for string: {s}")


# ANCHOR dumps
def dumps_json(obj, **kwargs):
    import json

    return json.dumps(obj, **kwargs)


def dumps_pickle(obj, **kwargs):
    import pickle

    return pickle.dumps(obj, **kwargs)


def dumps_csv(obj, **kwargs):
    import csv

    return csv.dumps(obj, **kwargs)


def dumps_toml(obj, **kwargs):
    import toml

    return toml.dumps(obj, **kwargs)


def dumps_yaml(obj, **kwargs):
    import yaml

    return yaml.dump(obj, **kwargs)


def dumps_xml(obj, **kwargs):
    import xml.etree.ElementTree as ET

    return ET.dumps(obj, **kwargs)
