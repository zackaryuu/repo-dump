import time as _time
import logging as _logging
import sys as _sys
from functools import cache as _cache
import os as _os
import functools as _functools


@_cache
def os_keyring():
    import platform

    """
    Returns an instance of the appropriate keyring backend based on the current operating system.

    This function uses the `platform.system()` function to determine the current operating system and then imports the appropriate keyring backend module. The following keyring backends are supported:
    - Windows: `keyring.backends.Windows.WinVaultKeyring`
    - macOS: `keyring.backends.macOS.Keyring`
    - Linux: `keyring.backends.SecretService.Keyring`

    The function is decorated with `@cache`, which means that the result of the first call to `os_keyring()` is cached and subsequent calls will return the cached result.

    Returns:
        An instance of the appropriate keyring backend.
    """
    if platform.system() == "Windows":
        from keyring.backends.Windows import WinVaultKeyring

        return WinVaultKeyring()
    elif platform.system() == "Darwin":
        from keyring.backends.macOS import Keyring

        return Keyring()
    elif platform.system() == "Linux":
        from keyring.backends.SecretService import Keyring

        return Keyring()


def unix_timestamp():
    return int(_time.time() * 1000)


def basic_debug(level=10):
    """
    Sets up basic logging configuration with the specified logging level and stream.

    Args:
        level (int, optional): The logging level to set. Defaults to logging.DEBUG.
    """
    _logging.basicConfig(level=level, stream=_sys.stdout)


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


def preserve_cwd(func):
    @_functools.wraps(func)
    def wrapper(*args, **kwargs):
        original_cwd = _os.getcwd()
        try:
            return func(*args, **kwargs)
        finally:
            _os.chdir(original_cwd)

    return wrapper


class classProperty(object):
    """
    A class that provides a descriptor for defining class-level properties.
    """

    def __init__(self, fget, fset=None):
        self.fget = fget
        self.fset = fset

    def __get__(self, obj, klass=None):
        if klass is None:
            klass = type(obj)
        return self.fget.__get__(obj, klass)()

    def __set__(self, obj, value):
        if not self.fset:
            raise AttributeError("can't set attribute")
        type_ = type(obj)
        return self.fset.__get__(obj, type_)(value)

    def setter(self, func):
        if not isinstance(func, (classmethod, staticmethod)):
            func = classmethod(func)
        self.fset = func
        return self
