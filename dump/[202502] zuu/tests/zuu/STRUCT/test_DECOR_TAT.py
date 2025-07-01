import pytest
from unittest.mock import patch
from src.zuu.STRUCT.DECOR.track_and_terminate import lifetime
import time

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
