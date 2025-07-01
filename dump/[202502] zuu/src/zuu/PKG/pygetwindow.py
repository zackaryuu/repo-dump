import typing
import pygetwindow as gw

def activate_wnd(wnd: gw.BaseWindow):
    """
    Activates the given window if it is not already active.

    Args:
        wnd (gw.Window): The window to activate.

    Returns:
        None

    Raises:
        None
    """
    try:
        if wnd.isActive:
            return
        wnd.activate()
    except gw.PyGetWindowException:
        pass


def get_window_pos(wnd: gw.BaseWindow) -> typing.Tuple[float, float, float, float]:
    """
    Get the position and size of the window.

    Args:
        wnd (gw.Window): The window from which to retrieve the position and size.

    Returns:
        typing.Tuple[float, float, float, float]: A tuple containing the left, top, width, and height of the window.
    """
    return (wnd.left, wnd.top, wnd.width, wnd.height)


def filter_visible_windows(
    wnds: typing.Iterable[gw.BaseWindow],
) -> typing.List[gw.BaseWindow]:
    rwnds = []
    for wnd in wnds:
        if wnd.height > 0 and wnd.width > 0:
            rwnds.append(wnd)
    return rwnds


def filter_titled_windows(
    wnds: typing.Iterable[gw.BaseWindow],
) -> typing.List[gw.BaseWindow]:
    """
    Filter non-titled windows.

    Args:
        wnds (typing.Iterable[gw.Window]): An iterable of windows to filter.

    Returns:
        typing.List[gw.Window]: A list of windows with titles.
    """
    rwnds = []
    for wnd in wnds:
        if wnd.title:
            rwnds.append(wnd)
    return rwnds
