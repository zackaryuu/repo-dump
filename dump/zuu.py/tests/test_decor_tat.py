import pytest
from unittest.mock import patch
from zuu.util_procLifetime import lifetime
import time
from typing import Any, Callable
from zuu.util_procLifetime import lifetime_run


@pytest.fixture
def mock_windows():
    with patch('pygetwindow.getAllWindows') as mock:
        yield mock

@pytest.fixture
def mock_processes():
    with patch('psutil.Process') as mock:
        yield mock

class TestLifetimeDecorator:
    def test_termination(self):

        @lifetime("100ms")
        def long_running():
            time.sleep(1)
            return "finished"

        result = long_running()
        assert result is None  # Function didn't finish

    def test_exception_propagation(self):
        @lifetime("1s")
        def error_func():
            raise ValueError("test error")

        with pytest.raises(ValueError, match="test error"):
            error_func()

    def test_normal_execution(self):
        @lifetime("100ms")
        def quick_func():
            return "done"

        assert quick_func() == "done"

class TestLifetimeRunBehavior:
    def test_termination_via_run(self):
        def long_process():
            time.sleep(1)
            return "finished"
            
        result = lifetime_run("100ms", long_process)
        assert result is None  # Process should be terminated

    def test_exception_propagation_via_run(self):
        def error_func():
            raise RuntimeError("run error")
            
        with pytest.raises(RuntimeError, match="run error"):
            lifetime_run("1s", error_func)

    def test_normal_execution_via_run(self):
        def quick_task():
            return "success"
            
        assert lifetime_run("100ms", quick_task) == "success"

    def test_args_kwargs_passing(self):
        def adder(a, b=0):
            return a + b
            
        assert lifetime_run("10ms", adder, 5, b=3) == 8

