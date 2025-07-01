import os
import re
import shutil
import tempfile
from functools import wraps
from typing import Callable, Dict, Optional, Union


def _verify_and_convert_paths(args, kwargs):
    """Helper function to verify and convert potential paths in args and kwargs"""
    converted_args = []
    for arg in args:
        if isinstance(arg, str) and os.path.exists(arg):
            converted_args.append(os.path.abspath(arg))
        elif isinstance(arg, list) and all(isinstance(x, str) for x in arg):
            if os.path.exists(arg[0]):
                converted_args.append([os.path.abspath(x) for x in arg])
            else:
                converted_args.append(arg)
        else:
            converted_args.append(arg)

    converted_kwargs = {}
    for key, value in kwargs.items():
        if isinstance(value, str) and os.path.exists(value):
            converted_kwargs[key] = os.path.abspath(value)
        elif isinstance(value, list) and all(isinstance(x, str) for x in value):
            if os.path.exists(value[0]):
                converted_kwargs[key] = [os.path.abspath(x) for x in value]
            else:
                converted_kwargs[key] = value
        else:
            converted_kwargs[key] = value

    return tuple(converted_args), converted_kwargs


def tempdir_op(
    path: Optional[str] = None,
    error_strategies: Optional[Dict[type, Union[str, Callable]]] = None,
    target_dir: Optional[str] = None,
    captures: Optional[list] = None,
):
    """
    Decorator that executes a function in a temporary directory and handles cleanup based on error strategies.

    Args:
        path (str, optional): Base path for operations. If None, will try to get from decorated function's first argument
        error_strategies (Dict[type, Union[str, Callable]], optional): Mapping of exception types to strategies
        target_dir (str, optional): Target directory for copying files. Defaults to path/debug
        captures (list, optional): List of patterns to capture on success. Defaults to ["*"]

    Strategies:
        "copyover": Copy all files from temp dir to target directory on error
        callable: Custom function to handle cleanup
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get path from decorator param or first function argument
            op_path = path
            if op_path is None:
                if not args:
                    raise ValueError(
                        "No path provided - must be specified in decorator or as first function argument"
                    )
                op_path = args[0]

            # Convert any path arguments to absolute paths
            args, kwargs = _verify_and_convert_paths(args, kwargs)

            # Create temp directory
            with tempfile.TemporaryDirectory() as temp_dir:
                original_dir = os.getcwd()
                os.chdir(temp_dir)

                try:
                    result = func(*args, **kwargs)

                    # On success, copy captured files if specified
                    patterns = captures if captures else ["*"]
                    target = target_dir if target_dir else op_path
                    os.makedirs(target, exist_ok=True)

                    for pattern in patterns:
                        for item in os.listdir(temp_dir):
                            if (
                                not pattern
                                or pattern == "*"
                                or re.match(pattern, item)
                            ):
                                
                                src = os.path.join(temp_dir, item)
                                dst = os.path.join(target, item)
                                if os.path.isdir(src):
                                    shutil.copytree(src, dst, dirs_exist_ok=True)
                                else:
                                    shutil.copy2(src, dst)

                    return result

                except Exception as e:
                    # Get error strategy if one exists for this exception type
                    strategy = None
                    if error_strategies:
                        for exc_type, strat in error_strategies.items():
                            if isinstance(e, exc_type):
                                strategy = strat
                                break

                    if strategy:
                        # Handle copyover strategy
                        if isinstance(strategy, str) and strategy.lower() == "copyover":
                            # Determine target directory
                            copy_target = (
                                target_dir
                                if target_dir
                                else os.path.join(op_path, "debug")
                            )
                            os.makedirs(copy_target, exist_ok=True)

                            # Copy all files from temp dir
                            for item in os.listdir(temp_dir):
                                src = os.path.join(temp_dir, item)
                                dst = os.path.join(copy_target, item)
                                if os.path.isdir(src):
                                    shutil.copytree(src, dst, dirs_exist_ok=True)
                                else:
                                    shutil.copy2(src, dst)

                        # Handle custom function strategy
                        elif callable(strategy):
                            strategy(temp_dir, e)

                    raise  # Re-raise the exception

                finally:
                    os.chdir(original_dir)

        return wrapper

    return decorator
