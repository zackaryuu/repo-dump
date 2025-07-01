import os
import json
import time
import pytest
from zuu.STRUCT.dict_with_autosave import DictWithAutosave

@pytest.fixture
def temp_json_file(tmp_path):
    """Fixture to create a temporary JSON file for testing."""
    file_path = tmp_path / "test_dict.json"
    # Ensure the parent directory exists
    file_path.parent.mkdir(parents=True, exist_ok=True)
    return str(file_path)

def test_init_with_new_file(temp_json_file):
    """Test initialization with a new file."""
    d = DictWithAutosave(temp_json_file)
    assert len(d) == 0
    assert os.path.exists(temp_json_file)
    
def test_init_with_initial_data(temp_json_file):
    """Test initialization with initial data."""
    # Ensure directory exists
    os.makedirs(os.path.dirname(temp_json_file), exist_ok=True)
    
    # Create empty file first
    with open(temp_json_file, 'w') as f:
        json.dump({}, f)
    
    initial_data = {"key1": "value1", "key2": "value2"}
    d = DictWithAutosave(temp_json_file, initial_data)
    assert dict(d) == initial_data
    
    # Verify file contents
    with open(temp_json_file, 'r') as f:
        saved_data = json.load(f)
    assert saved_data == initial_data

def test_basic_operations(temp_json_file):
    """Test basic dictionary operations."""
    d = DictWithAutosave(temp_json_file)
    
    # Test __setitem__
    d["key1"] = "value1"
    assert d["key1"] == "value1"
    
    # Test update
    d.update({"key2": "value2", "key3": "value3"})
    assert d["key2"] == "value2"
    assert d["key3"] == "value3"
    
    # Test pop
    value = d.pop("key2")
    assert value == "value2"
    assert "key2" not in d
    
    # Test __delitem__
    del d["key1"]
    assert "key1" not in d
    
    # Test popitem
    d["key4"] = "value4"
    key, value = d.popitem()
    assert key not in d
    
    # Test clear
    d.clear()
    assert len(d) == 0

def test_persistence(temp_json_file):
    """Test that data persists between instances."""
    d1 = DictWithAutosave(temp_json_file)
    d1["key1"] = "value1"
    
    # Create new instance and verify data
    d2 = DictWithAutosave(temp_json_file)
    assert d2["key1"] == "value1"

def test_external_modification(temp_json_file):
    """Test handling of external file modifications."""
    d1 = DictWithAutosave(temp_json_file)
    d1["key1"] = "value1"
    
    # Modify file externally
    time.sleep(0.1)  # Ensure modification time is different
    external_data = {"key2": "value2"}
    with open(temp_json_file, 'w') as f:
        json.dump(external_data, f)
    
    # Next operation should detect the change and reload
    d1["key3"] = "value3"
    assert d1["key2"] == "value2"
    assert d1["key3"] == "value3"
    assert "key1" not in d1

def test_invalid_json(temp_json_file):
    """Test handling of invalid JSON file."""
    # Create invalid JSON file
    with open(temp_json_file, 'w') as f:
        f.write("invalid json")
    
    # Should raise JSONDecodeError
    with pytest.raises(json.JSONDecodeError):
        DictWithAutosave(temp_json_file) 