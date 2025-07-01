from typing import Any, Callable, Optional, Dict
from zuu.io import load, dump
import os


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

        if change_detector is None:
            self.change_detector = self._default_change_detector
        else:
            self.change_detector = change_detector

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

        if cache_key not in cache:
            cache[cache_key] = current_mtime
            return False

        changed = current_mtime > cache[cache_key]
        cache[cache_key] = current_mtime
        return changed

    def __set_name__(self, owner, name):
        self.name = name

    def _resolve_path(self, obj) -> str:
        """Resolve the path from either string, callable or instance attribute"""
        if self._resolved_path is not None:
            return self._resolved_path

        if self._path is None:
            # Try to get path from instance
            if hasattr(obj, "path"):
                self._resolved_path = obj.path
            else:
                raise AttributeError(
                    "No path specified and instance has no 'path' attribute"
                )
        elif callable(self._path):
            self._resolved_path = self._path(obj)
        else:
            self._resolved_path = self._path

        return self._resolved_path

    def __get__(self, obj, objtype=None) -> Any:
        if obj is None:
            return self

        path = self._resolve_path(obj)

        if not path:
            raise ValueError("Path not properly set")

        # Convert path to string if it's a Path object
        path_str = str(path) if hasattr(path, "__fspath__") else path

        if self.change_detector(path_str, self._cache):
            # File changed externally, reload
            value = load(path_str, _throw_error=False)
            if value is not None:
                # Only update if load succeeded
                obj.__dict__[self.name] = value
                return value

        # Return cached value if exists
        if self.name in obj.__dict__:
            return obj.__dict__[self.name]

        # Initial load
        value = load(path_str, _throw_error=False)
        if value is not None:
            obj.__dict__[self.name] = value
        return value

    def __set__(self, obj, value):
        path = self._resolve_path(obj)
        obj.__dict__[self.name] = value

        if self.auto_sync:
            # Convert path to string if it's a Path object
            path_str = str(path) if hasattr(path, "__fspath__") else path

            # Only create directories if there's actually a directory path
            dirname = os.path.dirname(path_str)
            if dirname:  # Only create directories if there's a non-empty directory path
                os.makedirs(dirname, exist_ok=True)

            dump(value, path_str)
            # Update cache after saving
            cache_key = f"mtime:{path_str}"
            self._cache[cache_key] = os.path.getmtime(path_str)

            # Call callback if defined
            if hasattr(self, "_callback"):
                self._callback(obj, value)

    def callback(self, func):
        """
        Decorator to set a callback function that will be called after the property is set.
        The callback receives the instance and the new value as arguments.

        Example:
            @property.callback
            def on_change(self, new_value):
                print(f"Value changed to: {new_value}")
        """
        self._callback = func
        return self
