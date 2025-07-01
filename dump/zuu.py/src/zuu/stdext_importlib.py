import importlib.util
import sys
from pathlib import Path
import typing

__all__: list[str] = ["import_file"]

def import_file(file_path: str, package_set: str = None) -> typing.Any:
    """
    Import a Python file as a module.

    Args:
        file_path (str): The path to the Python file to import.

    Returns:
        Any: The imported module.

    Raises:
        ImportError: If the file cannot be imported.
    """
    file_path = Path(file_path).resolve()
    module_name = file_path.stem

    # Add the parent directory to sys.path
    parent_dir = file_path.parent
    sys.path.insert(0, str(parent_dir))

    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None:
        raise ImportError(
            f"Could not load spec for module {module_name} from {file_path}"
        )

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module

    if spec.loader is None:
        raise ImportError(f"Could not load module {module_name} from {file_path}")

    # Set the package context for relative imports
    module.__package__ = str(module_name) if package_set is None else package_set
    spec.loader.exec_module(module)
    return module

class LazyFileImport:
    def __init__(self, file_path: str, package_set: str = None):
        self.__xxxx = None   
        self.__xxxx_file_path = file_path
        self.__xxxx_package_set = package_set
        
    def __getattribute__(self, name : str) -> typing.Any:
        if name in ["__xxxx_file_path", "__xxxx_package_set"]:
            return super().__getattribute__(name)
        
        if hasattr(self.__xxxx, name):
            if self.__xxxx is None:
                self.__xxxx = import_file(self.__xxxx_file_path, self.__xxxx_package_set)
            return getattr(self.__xxxx, name)
        return super().__getattribute__(name)

    