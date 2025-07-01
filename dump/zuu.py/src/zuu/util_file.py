import os as _os
import stat as _stat
import typing as _typing
import re as _re


# reading
def read_first_byte(path: str):
    with open(path, "rb") as f:
        return f.read(1)


def read_last_byte(path: str):
    with open(path, "rb") as f:
        # Get file size
        f.seek(0, 2)
        size = f.tell()
        if size == 0:
            return b""
        # Read last byte
        f.seek(-1, 2)
        return f.read(1)


def read_first_and_last_byte(path: str):
    with open(path, "rb") as f:
        first = f.read(1)
        # Get file size
        f.seek(0, 2)
        size = f.tell()
        if size == 0:
            return b"", b""
        # Read last byte
        f.seek(-1, 2)
        last = f.read(1)
        return first, last


# iter by chunk generator
def iter_by_chunk(path: str, chunk_size: int = 4096):
    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk


# has hidden
def has_hidden_attribute(filepath):
    """
    Check if a file has the hidden attribute.

    Parameters:
        filepath (str): The path to the file.

    Returns:
        bool: True if the file has the hidden attribute, False otherwise.
    """
    return bool(_os.stat(filepath).st_file_attributes & _stat.FILE_ATTRIBUTE_HIDDEN)


# common file op
def determine_file_type(path: str):
    path_extension = _os.path.splitext(path)[1]
    match path_extension:
        case ".json":
            return "json"
        case ".yaml" | ".yml":
            return "yaml"
        case ".toml":
            return "toml"
        case ".xml":
            return "xml"
        case ".csv":
            return "csv"
        case ".pickle" | ".pkl":
            return "pickle"
        case _:
            return "plain"


deserialize_methods = {
    "json": lambda x: __import__("json").loads(x),
    "yaml": lambda x: __import__("yaml").safe_load(x),
    "toml": lambda x: __import__("toml").loads(x),
    "xml": lambda x: __import__("xml.etree.ElementTree").fromstring(x),
    "csv": lambda x: __import__("csv").reader(x),
    "pickle": lambda x: __import__("pickle").loads(x),
}


def deserialize(
    data: str,
    file_type: str,
    deserialize_methods: dict = deserialize_methods,
):
    if file_type == "plain":
        return data

    if file_type not in deserialize_methods:
        raise ValueError(f"Unsupported file type: {file_type}")

    return deserialize_methods[file_type](data)


serialize_methods = {
    "json": lambda x, **kwargs: __import__("json").dumps(x, **kwargs),
    "yaml": lambda x, **kwargs: __import__("yaml").dump(x, **kwargs),
    "toml": lambda x, **kwargs: __import__("toml").dumps(x, **kwargs),
    "xml": lambda x, **kwargs: __import__("xml.etree.ElementTree").tostring(x, **kwargs),
    "csv": lambda x, **kwargs: __import__("csv").writer(x, **kwargs),
    "pickle": lambda x, **kwargs: __import__("pickle").dumps(x, **kwargs),
}


def serialize(
    data: any,
    file_type: str,
    serialize_methods: dict = serialize_methods,
    **kwargs
):
    if file_type == "plain":
        return data

    if file_type not in serialize_methods:
        raise ValueError(f"Unsupported file type: {file_type}")

    return serialize_methods[file_type](data, **kwargs)


def load(
    path: str,
    encoding: str = "utf-8",
    auto_deserialize: bool = True,
):
    if not _os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")

    file_data = open(path, "r", encoding=encoding).read()

    if auto_deserialize:
        file_type = determine_file_type(path)
        return deserialize(file_data, file_type)

    return file_data


def save(
    data: any,
    path: str,
    file_type: str | None = None,
    encoding: str = "utf-8",
    **kwargs
):
    if file_type is None:
        file_type = determine_file_type(path)

    serialized_data = serialize(data, file_type, **kwargs)

    with open(path, "w", encoding=encoding) as f:
        f.write(serialized_data)


def touch(
    path: str, initial_data: any = None, initial_factory: _typing.Callable = None
):
    if _os.path.exists(path):
        return

    if initial_factory is not None:
        initial_data = initial_factory()

    if initial_data is None:
        filetype = determine_file_type(path)
        if filetype == "plain":
            initial_data = ""
        else:
            initial_data = {}

    save(initial_data, path)


#!SECTION
def scan_pathes(pathes: list[str], depth: int = 1) -> list[str]:
    """
    Scan directories and return a list of all paths up to the specified depth.

    Args:
        pathes: List of root directories to scan
        depth: Search depth:
            - 0: Only match the root directories themselves
            - 1: Match immediate children (default)
            - 2: Match children and grandchildren
            - -1: Unlimited depth
    """

    if depth == 0:
        return pathes

    results = []
    queue = []

    # Initialize queue with root directories and depth 0
    for path in pathes:
        abs_path = _os.path.abspath(path)
        queue.append((abs_path, 0))

    while queue:
        current_path, current_depth = queue.pop(0)

        # Skip if we're beyond depth limit (unless depth is -1)
        if depth != -1 and current_depth > depth:
            continue

        results.append(current_path)

        # Process children if within depth limit and is directory
        if _os.path.isdir(current_path) and (depth == -1 or current_depth < depth):
            try:
                for entry in _os.listdir(current_path):
                    full_path = _os.path.join(current_path, entry)
                    queue.append((full_path, current_depth + 1))
            except PermissionError:
                continue

    return results


def path_match(
    pathes: list[str], matches: _typing.List[str], depth: int = 1
) -> list[str]:
    """
    Match files in directory hierarchies against patterns with depth control.

    Args:
        pathes: List of root directories to search
        matches: List of patterns (regex or *pattern syntax)
        depth: Search depth (handled by scan_pathes):
            - 0: Only match the root directories themselves
            - 1: Match immediate children (default)
            - 2: Match children and grandchildren
            - -1: Unlimited depth
    """
    # Get all paths within depth limit first
    eligible_pathes = scan_pathes(pathes, depth)

    # Compile patterns only once
    compiled = []
    for pattern in matches:
        regex = _re.escape(pattern).replace(r"\*", ".*")
        compiled.append(_re.compile(regex))

    # Match against eligible paths
    results = []
    common_root = _os.path.commonpath(eligible_pathes) if eligible_pathes else ""
    for path in eligible_pathes:
        # Normalize paths to Unix-style for pattern matching
        base_name = _os.path.basename(path)
        rel_path = _os.path.relpath(path, common_root).replace(_os.sep, "/")

        # Check against all patterns
        for pattern in compiled:
            if pattern.search(rel_path) or pattern.search(base_name):
                results.append(path)
                break

    return results


def listdir_match(path: str, matches: _typing.List[str], depth: int = 0) -> list[str]:
    return path_match(_os.listdir(path), matches, depth)
