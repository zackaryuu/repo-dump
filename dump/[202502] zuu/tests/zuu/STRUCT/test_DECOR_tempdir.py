import os
import pytest
from zuu.STRUCT.DECOR.tempdir import _verify_and_convert_paths, tempdir_op

# Test fixtures
@pytest.fixture
def temp_test_dir(tmp_path):
    """Create a temporary test directory with some files"""
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()
    (test_dir / "test_file.txt").write_text("test content")
    (test_dir / "test_file2.txt").write_text("test content 2")
    return str(test_dir)

# Test _verify_and_convert_paths
def test_verify_and_convert_paths(temp_test_dir):
    # Test with single path
    args = [temp_test_dir]
    kwargs = {"output": temp_test_dir}
    
    conv_args, conv_kwargs = _verify_and_convert_paths(args, kwargs)
    
    assert conv_args[0] == os.path.abspath(temp_test_dir)
    assert conv_kwargs["output"] == os.path.abspath(temp_test_dir)
    
    # Test with list of paths
    args = [[str(temp_test_dir), str(temp_test_dir)]]
    conv_args, _ = _verify_and_convert_paths(args, {})
    
    assert all(p == os.path.abspath(temp_test_dir) for p in conv_args[0])
    
    # Test with non-existent paths
    args = ["non_existent_path"]
    conv_args, _ = _verify_and_convert_paths(args, {})
    
    assert conv_args[0] == "non_existent_path"

# Test tempdir_op decorator
def test_tempdir_op_basic(temp_test_dir):
    @tempdir_op()
    def sample_function(path):
        assert os.getcwd() != path  # Should be in temp directory
        with open("output.txt", "w") as f:
            f.write("test")
        return "success"
    
    result = sample_function(temp_test_dir)
    assert result == "success"
    assert os.path.exists(os.path.join(temp_test_dir, "output.txt"))

def test_tempdir_op_with_captures(temp_test_dir):
    @tempdir_op(captures=["test_*"])
    def sample_function(path):
        with open("test_1.txt", "w") as f:
            f.write("test1")
        with open("ignore.txt", "w") as f:
            f.write("ignore")
        return "success"
    
    sample_function(temp_test_dir)
    assert os.path.exists(os.path.join(temp_test_dir, "test_1.txt"))
    assert not os.path.exists(os.path.join(temp_test_dir, "ignore.txt"))

def test_tempdir_op_error_handling(temp_test_dir):
    error_strategies = {
        ValueError: "copyover"
    }
    
    @tempdir_op(error_strategies=error_strategies)
    def failing_function(path):
        with open("error_file.txt", "w") as f:
            f.write("error content")
        raise ValueError("Test error")
    
    with pytest.raises(ValueError):
        failing_function(temp_test_dir)
    
    # Check if file was copied to debug directory
    debug_file = os.path.join(temp_test_dir, "debug", "error_file.txt")
    assert os.path.exists(debug_file)
    with open(debug_file) as f:
        assert f.read() == "error content"

def test_tempdir_op_custom_error_handler(temp_test_dir):
    def custom_handler(temp_dir, error):
        with open(os.path.join(temp_test_dir, "error_log.txt"), "w") as f:
            f.write(f"Error in {temp_dir}: {str(error)}")
    
    error_strategies = {
        ValueError: custom_handler
    }
    
    @tempdir_op(error_strategies=error_strategies)
    def failing_function(path):
        raise ValueError("Test error")
    
    with pytest.raises(ValueError):
        failing_function(temp_test_dir)
    
    assert os.path.exists(os.path.join(temp_test_dir, "error_log.txt")) 