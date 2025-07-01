import re
from functools import wraps
import datetime
from ..time_parse import time_parse
from typing import Union, Callable, Any, Optional, Set
import psutil
import pygetwindow as gw
import threading
import ctypes

def glob_to_regex(glob_pattern: str) -> str:
    """Convert glob pattern to regex pattern"""
    return glob_pattern.replace('*', '.*').replace('?', '.').lower()

def match_windows(patterns: Union[bool, list[str]]) -> Set[int]:
    """Return set of window handles matching patterns"""
    if patterns is None:
        return set()
        
    windows = gw.getAllWindows()
    if patterns is True:
        return {win._hWnd for win in windows}
        
    regex_patterns = [glob_to_regex(p) for p in patterns]
    return {
        win._hWnd for win in windows
        if any(re.search(p, win.title.lower()) for p in regex_patterns)
    }

def match_processes(patterns: Union[bool, list[str]]) -> Set[int]:
    """Return set of process PIDs matching patterns"""
    if patterns is None:
        return set()
        
    procs = psutil.Process().children(recursive=True)
    if patterns is True:
        return {proc.pid for proc in procs}
        
    regex_patterns = [glob_to_regex(p) for p in patterns]
    matched = set()
    for proc in procs:
        try:
            name = proc.name().lower()
            cmdline = ' '.join(proc.cmdline()).lower()
            if any(re.search(p, name) or re.search(p, cmdline) for p in regex_patterns):
                matched.add(proc.pid)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return matched

def cleanup(
    windows: Optional[Union[bool, list[str]]] = None,
    processes: Optional[Union[bool, list[str]]] = None,
    new_only: bool = False
) -> Callable:
    """Decorator to clean up windows/processes with proper state diffing"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Determine which resources to track/clean
            use_windows = windows not in (None, False)
            use_procs = processes not in (None, False)

            # Pre-execution state (only track if needed)
            pre_wins = set()
            pre_procs = set()
            if new_only:
                if use_windows:
                    pre_wins = match_windows(windows)
                if use_procs:
                    pre_procs = match_processes(processes)

            # Execute function
            result = func(*args, **kwargs)

            # Post-execution state (only check if needed)
            post_wins = match_windows(windows) if use_windows else set()
            post_procs = match_processes(processes) if use_procs else set()

            # Calculate targets
            win_targets = (post_wins - pre_wins) if new_only else post_wins
            proc_targets = (post_procs - pre_procs) if new_only else post_procs

            # Resource cleanup
            if use_windows:
                for hwnd in win_targets:
                    try:
                        gw.Win32Window(hwnd).close()
                    except Exception:
                        pass

            if use_procs:
                for pid in proc_targets:
                    try:
                        proc = psutil.Process(pid)
                        proc.terminate()
                        proc.wait(timeout=3)
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                        try:
                            proc.kill()
                        except Exception:
                            pass

            return result
        return wrapper
    return decorator

def lifetime(
    timestr: str,
):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get target termination time and ensure it's a timestamp
            target_time : datetime.datetime = time_parse(timestr)
            
            result = [None]
            exception = [None]
            thread_id = None

            def async_raise(target_tid, exc_type):
                """Raises an exception in the target thread"""
                res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
                    ctypes.c_long(target_tid),
                    ctypes.py_object(exc_type)
                )
                if res == 0:
                    raise ValueError("Invalid thread ID")
                elif res != 1:
                    ctypes.pythonapi.PyThreadState_SetAsyncExc(target_tid, None)
                    raise SystemError("Failed to set exception")

            def run_func():
                nonlocal thread_id
                thread_id = threading.get_ident()
                try:
                    result[0] = func(*args, **kwargs)
                except Exception as e:
                    exception[0] = e

            thread = threading.Thread(target=run_func)
            thread.daemon = True
            thread.start()
            
            wait_time = max((target_time - datetime.datetime.now()).total_seconds(), 0)
            thread.join(wait_time)
            
            if thread.is_alive():
                try:
                    async_raise(thread_id, SystemExit)
                    thread.join(0.1)  # Give it a moment to clean up
                except Exception:
                    pass
                return None
                
            if exception[0] is not None:
                raise exception[0]
                
            return result[0]

        return wrapper
    
    return decorator
