import hashlib as _hashlib
import os as _os
import stat as _stat
import functools as _functools
import logging as _logging
import sys as _sys

def sha256(string: str) -> str:
    hasher = _hashlib.sha256()
    if not _os.path.exists(string):
        return hasher(string).hexdigest()

    with open(string, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            chunk = chunk.replace(b"\r\n", b"\n")
            hasher.update(chunk)
    return hasher.hexdigest()

# OS

def has_hidden_attribute(filepath):
    """
    Check if a file has the hidden attribute.

    Parameters:
        filepath (str): The path to the file.

    Returns:
        bool: True if the file has the hidden attribute, False otherwise.
    """
    return bool(_os.stat(filepath).st_file_attributes & _stat.FILE_ATTRIBUTE_HIDDEN)


def preserve_cwd(func):
    @_functools.wraps(func)
    def wrapper(*args, **kwargs):
        original_cwd = _os.getcwd()
        try:
            return func(*args, **kwargs)
        finally:
            _os.chdir(original_cwd)

    return wrapper

# pywin32

def get_pid_from_hwnd(hwnd):
    """
    Get the process ID given the handle of a window.

    Args:
        hwnd (int or gw.Win32Window): The handle of the window. If it is an instance of gw.Win32Window, its handle will be extracted.

    Returns:
        int or None: The process ID of the window, or None if an error occurred.
    """
    import pygetwindow as gw
    if not isinstance(hwnd, int):
        assert isinstance(hwnd, gw.Win32Window)
        hwnd = hwnd._hWnd

    try:
        import win32process
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        return pid
    except Exception as e:
        print(f"Error: {e}")
        return None
    
#logging



def basic_debug(level=10):
    """
    Sets up basic logging configuration with the specified logging level and stream.

    Args:
        level (int, optional): The logging level to set. Defaults to logging.DEBUG.
    """
    _logging.basicConfig(level=level, stream=_sys.stdout)
