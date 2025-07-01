def get_overload_signatures(func):
    import inspect
    from typing import get_overloads

    """
    A function that yields the signature of each overload function in the given function.
    """
    overloads = get_overloads(func)
    for overloadFunc in overloads:
        yield inspect.signature(overloadFunc)


def bind_overload(overloadFunc, *args, **kwargs):
    """
    A function that binds the overload function with the given arguments and keyword arguments.
    """
    for sig in get_overload_signatures(overloadFunc):
        try:
            return sig.bind(*args, **kwargs).arguments
        except TypeError:
            pass
