
from datetime import datetime
from ..time_parse import time_parse

class timedProperty:
    """
    A descriptor that creates a property that expires after the specified duration.
    
    Args:
        duration: Time duration string (e.g. "5m", "1h", "30s") parsed by time_parse
        
    The cached value and expiry time are stored in the descriptor rather than on the instance.
    """
    def __init__(self, duration: str):
        self.duration = duration
        self.name = None
        self._cached_value = None
        self._expiry_time = None
        
    def __call__(self, func):
        self.func = func
        self.name = func.__name__
        return self
        
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
            
        # Check if cache is valid
        now = datetime.now()
        if self._cached_value is None or self._expiry_time is None or now >= self._expiry_time:
            # Cache miss - compute new value and expiry
            self._cached_value = self.func(obj)
            self._expiry_time = time_parse(self.duration)
            
        # Return cached value
        return self._cached_value

class timedClassProperty(object):
    """
    A descriptor that creates a class-level property that expires after the specified duration.
    
    Similar to timed_property but works at the class level rather than instance level.
    The cached value and expiry time are stored in the descriptor rather than on the class.
    """
    
    def __init__(self, fget, duration, fset=None):
        """
        Args:
            fget: Getter function
            duration: Time duration string (e.g. "5m", "1h", "30s") parsed by time_parse
            fset: Optional setter function
        """
        self.fget = fget
        self.fset = fset
        self.duration = duration
        self._cached_value = None
        self._expiry_time = None

    def __get__(self, obj, klass=None):
        if klass is None:
            klass = type(obj)
            
        # Check if cache is valid
        now = datetime.now()
        if self._cached_value is None or self._expiry_time is None or now >= self._expiry_time:
            # Cache miss - compute new value and expiry
            self._cached_value = self.fget.__get__(obj, klass)()
            self._expiry_time = time_parse(self.duration)
            
        return self._cached_value

    def __set__(self, obj, value):
        if not self.fset:
            raise AttributeError("can't set attribute")
        type_ = type(obj)
        self._cached_value = self.fset.__get__(obj, type_)(value)
        self._expiry_time = time_parse(self.duration)

    def setter(self, func):
        if not isinstance(func, (classmethod, staticmethod)):
            func = classmethod(func)
        self.fset = func
        return self
