from typing import Any, Callable, Optional, Dict
from zuu.util_file import load, save, touch
import os
import json


class fileProperty:
    """
    A descriptor that automatically loads and saves data to a file.
    Similar to property but handles file I/O automatically.
    """

    def __init__(
        self,
        path: Optional[str | Callable] = None,
        auto_sync: bool = True,
        change_detector: Optional[Callable[[str, Dict], bool]] = None,
    ):
        """
        Initialize the file property descriptor.

        Args:
            path: File path or callable that returns the file path
            auto_sync: Whether to automatically save changes back to file
            change_detector: Optional function to detect if file changed externally.
                           Takes file path and cache dict as arguments and returns bool.
                           Default checks modification time.
        """
        self._path = path
        self.auto_sync = auto_sync
        self.name = None
        self._cache = {}
        self._resolved_path = None
        self.change_detector = change_detector or self._default_change_detector
        self._callbacks = []

    def _get_cache_key(self, path: str) -> str:
        """Generate a unique cache key for a path and property"""
        return f"{self.__class__.__name__}:{id(self)}:{path}"

    @staticmethod
    def _default_change_detector(path: str, cache: Dict) -> bool:
        """Default change detection using file modification time"""
        if not os.path.exists(path):
            return False

        cache_key = f"mtime:{path}"
        current_mtime = os.path.getmtime(path)
        
        if cache_key not in cache or current_mtime > cache[cache_key]:
            cache[cache_key] = current_mtime
            return True
        return False

    def __set_name__(self, owner, name):
        self.name = name
        self.owner = owner  # Store the owner class

    def _resolve_path(self, obj) -> str:
        """Resolve the path from various sources"""
        if obj is None:
            # Class-level access, use the owner class
            resolving_obj = self.owner
        else:
            resolving_obj = obj

        if self._resolved_path is None:
            if self._path is None:
                if hasattr(resolving_obj, "path"):
                    self._resolved_path = resolving_obj.path
                else:
                    raise AttributeError("Missing path specification")
            else:
                self._resolved_path = self._path(resolving_obj) if callable(self._path) else self._path
        return self._resolved_path

    def __get__(self, obj, objtype=None) -> Any:
        # Handle class-level access
        if obj is None:
            obj = self.owner  # Use the class itself as the storage object
        
        path = self._resolve_path(obj)
        path_str = str(path) if hasattr(path, "__fspath__") else path
        
        # Check if we need to refresh the data
        if self.name in obj.__dict__:
            if self.change_detector(path_str, self._cache):
                self._load_and_store(obj, path_str)
        else:
            self._load_and_store(obj, path_str)
            
        return obj.__dict__[self.name]

    def _load_and_store(self, obj, path_str):
        """Load data from file and store in instance dict"""
        try:
            # Use touch to ensure file exists with proper structure
            touch(path_str, initial_factory=lambda: {})
            
            # Load normally after ensuring file exists
            obj.__dict__[self.name] = load(path_str)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            # Handle edge cases where file creation raced with other processes
            obj.__dict__[self.name] = {}
            save({}, path_str)
        except Exception as e:
            raise AttributeError(
                f"Failed to load data from {path_str}. Error: {str(e)}"
            ) from e

    def __set__(self, obj, value):
        # Handle class-level assignment through metaclass
        if obj is None:
            # Class-level assignment not supported directly
            raise AttributeError("Cannot set class-level fileProperty directly")
        
        # Rest of existing __set__ implementation
        path = self._resolve_path(obj)
        path_str = str(path) if hasattr(path, "__fspath__") else path
        
        # Store value and save to file
        obj.__dict__[self.name] = value
        
        if self.auto_sync:
            os.makedirs(os.path.dirname(path_str), exist_ok=True)
            save(value, path_str)
            self._cache[f"mtime:{path_str}"] = os.path.getmtime(path_str)
            
            for callback in self._callbacks:
                callback(obj, value)

    def callback(self, func):
        """Register multiple callbacks to be called when the value changes"""
        self._callbacks.append(func)
        return self
