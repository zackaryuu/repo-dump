import os
import json
from typing import Any, Dict, Optional


class DictWithAutosave(dict):
    """
    A dictionary that automatically saves changes to a file and monitors for external modifications.
    """

    def __init__(self, path: str, initial_data: Optional[Dict] = None):
        """
        Initialize the auto-saving dictionary.

        Args:
            path (str): Path to the JSON file for persistence
            initial_data (Dict, optional): Initial dictionary data
        """
        self._path = path
        self._last_mtime = 0

        # Create parent directory if it doesn't exist
        os.makedirs(os.path.dirname(path), exist_ok=True)

        if initial_data is not None:
            super().__init__(initial_data)
            self._save()  # Save initial data to file
        else:
            self._load()

    def _load(self) -> None:
        """Load data from file if it exists and update last modified time."""
        if os.path.exists(self._path):
            with open(self._path, "r") as f:
                super().clear()  # Clear existing data first
                super().update(json.load(f))
            self._last_mtime = os.path.getmtime(self._path)
        else:
            super().clear()
            self._save()

    def _save(self) -> None:
        """Save current dictionary state to file."""
        with open(self._path, "w") as f:
            json.dump(dict(self), f, indent=2)
        self._last_mtime = os.path.getmtime(self._path)

    def _check_and_reload(self) -> None:
        """Check if file was modified externally and reload if necessary."""
        if os.path.exists(self._path):
            current_mtime = os.path.getmtime(self._path)
            if current_mtime > self._last_mtime:
                self._load()

    def __setitem__(self, key: str, value: Any) -> None:
        """Override setitem to auto-save on changes."""
        self._check_and_reload()
        super().__setitem__(key, value)
        self._save()

    def __delitem__(self, key: str) -> None:
        """Override delitem to auto-save on changes."""
        self._check_and_reload()
        super().__delitem__(key)
        self._save()

    def update(self, *args, **kwargs) -> None:
        """Override update to auto-save on changes."""
        self._check_and_reload()
        super().update(*args, **kwargs)
        self._save()

    def clear(self) -> None:
        """Override clear to auto-save on changes."""
        self._check_and_reload()
        super().clear()
        self._save()

    def pop(self, key: str, default: Any = None) -> Any:
        """Override pop to auto-save on changes."""
        self._check_and_reload()
        result = super().pop(key, default)
        self._save()
        return result

    def popitem(self) -> tuple:
        """Override popitem to auto-save on changes."""
        self._check_and_reload()
        result = super().popitem()
        self._save()
        return result
