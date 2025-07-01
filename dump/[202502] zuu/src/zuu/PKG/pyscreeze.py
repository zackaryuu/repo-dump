
class Pyscreeze:
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

    @staticmethod
    def fullWin32Screenshot(imageFilename=None, region=None, allScreens=True):
        from pyscreeze import _screenshot_win32

        return _screenshot_win32(imageFilename, region, allScreens)

    overloaded: bool = False

    @staticmethod
    def overloadScreenshotWin32():
        import pyscreeze as pyscreeze
        import logging as logging

        pyscreeze._screenshot_win32 = Pyscreeze.fullWin32Screenshot
        logging.info("overwritten pyscreeze._screenshot_win32")
        Pyscreeze.overloaded = True

    @staticmethod
    def boxcenter(box):
        """
        Calculate the center coordinates of the given box.

        Parameters:
            box : tuple or Box
                The input box for which to calculate the center coordinates.

        Returns:
            Point
                The center coordinates of the box as a Point object.
        """

        if isinstance(box, tuple):
            return Pyscreeze.center(box)
        return Pyscreeze.Point(box.left + box.width / 2, box.top + box.height / 2)
