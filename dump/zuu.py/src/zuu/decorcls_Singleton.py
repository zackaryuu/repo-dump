def singleton_factory(cls=None, *, by_var=None):
    """
    A factory function that creates singleton classes.

    Args:
        cls: The class to make into a singleton
        by_var (str, optional): Variable name to use for instance mapping.
                              If None, only one instance is allowed.

    Returns:
        The modified class with singleton behavior
    """

    def wrap(cls):
        # Define metaclass based on whether by_var is specified
        if by_var is None:

            class SingletonMeta(type):
                _instance = None

                def __call__(cls, *args, **kwargs):
                    if cls._instance is None:
                        cls._instance = super().__call__(*args, **kwargs)
                    return cls._instance

        else:

            class SingletonMeta(type):
                _instances = {}

                def __call__(cls, *args, **kwargs):
                    # Check if the by_var parameter is provided
                    if by_var not in kwargs and not args:
                        raise TypeError(f"Missing required parameter '{by_var}'")

                    # Get the key from kwargs or args
                    key = kwargs.get(by_var) if by_var in kwargs else args[0]

                    if key not in cls._instances:
                        cls._instances[key] = super().__call__(*args, **kwargs)
                    return cls._instances[key]

        # Create new class with the singleton metaclass
        return SingletonMeta(cls.__name__, (cls,), dict(cls.__dict__))

    # Handle both @singleton_factory and @singleton_factory(by_var='name') syntax
    if cls is None:
        return wrap
    return wrap(cls)
