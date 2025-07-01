
from zuu.etc import classProperty
import pyscreeze as _pyscreeze
import logging as _logging

class PyScreeze:
    class OldImports:
        from pyscreeze import (  # noqa: E402
            center as center,
            locateAll as locateAll,
            locateAllOnScreen as locateAllOnScreen,
            locateCenterOnScreen as locateCenterOnScreen,
            locateOnScreen as locateOnScreen,
            locateOnWindow as locateOnWindow,
            pixel as pixel,
            pixelMatchesColor as pixelMatchesColor,
            screenshot as screenshot,

        )

        screenshot_win32 = _pyscreeze._screenshot_win32


    @staticmethod
    def fullWin32Screenshot(imageFilename=None, region=None, allScreens=True):
        from pyscreeze import _screenshot_win32

        return _screenshot_win32(imageFilename, region, allScreens)

    __enable_overload = False

    @classProperty
    def overload(cls, value):
        if value:
            import pyscreeze as pyscreeze

            cls._old_screenshot_win32 = pyscreeze._screenshot_win32
            pyscreeze._screenshot_win32 = cls.fullWin32Screenshot
            _logging.info("overwritten pyscreeze._screenshot_win32")
        else:
            pyscreeze._screenshot_win32 = cls._old_screenshot_win32
            _logging.info("restored pyscreeze._screenshot_win32")

        cls.__enable_overload = value

