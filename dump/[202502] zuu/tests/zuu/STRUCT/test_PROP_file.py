import pytest
import os
import time
from zuu.STRUCT.PROP.file import fileProperty

class TestClass:
    test_prop = fileProperty("tests/test.json")
    
    @test_prop.callback
    def on_prop_change(self, value):
        self.last_callback_value = value

def test_basic_operations(tmp_path):
    """Test basic get/set operations"""
    test_file = tmp_path / "tests" / "test.json"
    
    class TestObj:
        prop = fileProperty(test_file)
    
    obj = TestObj()
    
    # Test setting value
    obj.prop = {"test": 123}
    assert obj.prop == {"test": 123}
    
    # Verify file was created with correct content
    assert os.path.exists(test_file)
    
def test_callback(tmp_path):
    """Test callback functionality"""
    #test_file = tmp_path / "test.json"
    obj = TestClass()
    obj.test_prop = {"data": 42}
    
    assert hasattr(obj, 'last_callback_value')
    assert obj.last_callback_value == {"data": 42}

def test_external_changes(tmp_path):
    """Test detection of external file changes"""
    test_file = tmp_path / "tests" / "test.json"
    
    class TestObj:
        prop = fileProperty(test_file)
    
    obj = TestObj()
    obj.prop = {"original": 123}
    
    # Simulate external file modification
    time.sleep(0.1)  # Ensure modification time is different
    with open(test_file, 'w') as f:
        f.write('{"modified": 456}')
    
    # Should detect change and reload
    assert obj.prop == {"modified": 456}

def test_path_resolution(tmp_path):
    """Test different path resolution methods"""
    test_file = tmp_path /  "tests" / "test.json"
    
    # Test callable path
    def get_path(obj):
        return str(test_file)
    
    class TestObjCallable:
        prop = fileProperty(get_path)
    
    obj1 = TestObjCallable()
    obj1.prop = {"test": "callable"}
    assert obj1.prop == {"test": "callable"}
    
    # Test instance path attribute
    class TestObjInstance:
        prop = fileProperty()
        def __init__(self):
            self.path = str(test_file)
    
    obj2 = TestObjInstance()
    obj2.prop = {"test": "instance"}
    assert obj2.prop == {"test": "instance"}

def test_auto_sync(tmp_path):
    """Test auto_sync functionality"""
    test_file = tmp_path /  "tests" / "test.json"
    
    class TestObj:
        prop = fileProperty(test_file, auto_sync=False)
    
    obj = TestObj()
    obj.prop = {"test": "no_sync"}
    
    # File should not exist since auto_sync is False
    assert not os.path.exists(test_file)

def test_missing_path():
    """Test error handling for missing path"""
    class TestObj:
        prop = fileProperty()
    
    obj = TestObj()
    with pytest.raises(AttributeError):
        obj.prop = {"test": "error"} 