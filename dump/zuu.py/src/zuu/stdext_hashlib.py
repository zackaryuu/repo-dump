import hashlib
from zuu.util_file import iter_by_chunk


def sha256_by_chunk(path: str):
    hash = hashlib.sha256()
    for chunk in iter_by_chunk(path):
        hash.update(chunk)
    return hash.hexdigest()


def md5_by_chunk(path: str):
    hash = hashlib.md5()
    for chunk in iter_by_chunk(path):
        hash.update(chunk)
    return hash.hexdigest()


def hash_by_chunk(path: str, hash_type: str):
    hash = hashlib.new(hash_type)
    for chunk in iter_by_chunk(path):
        hash.update(chunk)
    return hash.hexdigest()
