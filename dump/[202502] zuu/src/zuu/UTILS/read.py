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
