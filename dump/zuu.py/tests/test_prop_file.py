import pytest
import os
import time
from zuu.prop_file import fileProperty

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

def test_local_updates(tmp_path):
    """Test multiple local updates and synchronization"""
    test_file = tmp_path / "tests" / "local_updates.json"
    
    class TestObj:
        prop = fileProperty(test_file)
        
        @prop.callback
        def on_prop_change(self, value):
            self.callback_count = getattr(self, 'callback_count', 0) + 1

    obj = TestObj()
    
    # Initial set
    obj.prop = {"version": 1}
    assert obj.prop == {"version": 1}
    assert obj.callback_count == 1
    
    # Update with new value
    obj.prop = {"version": 2, "data": "test"}
    assert obj.prop["version"] == 2
    assert obj.callback_count == 2
    
    # Verify file content
    with open(test_file) as f:
        assert f.read() == '{"version": 2, "data": "test"}'

def test_concurrent_modifications(tmp_path):
    """Test local changes overriding external changes"""
    test_file = tmp_path / "tests" / "concurrent.json"
    
    class TestObj:
        prop = fileProperty(test_file)
    
    obj = TestObj()
    obj.prop = {"value": "initial"}
    
    # Make external change
    with open(test_file, 'w') as f:
        f.write('{"value": "external"}')
    
    # Make local change that should override
    obj.prop = {"value": "local"}
    
    # Verify local change persists
    assert obj.prop == {"value": "local"}
    with open(test_file) as f:
        assert f.read() == '{"value": "local"}'

def test_class_property(tmp_path):
    """Test using fileProperty as a class-level property"""
    test_file = tmp_path / "class_prop.json"
    
    class ClassConfig:
        # Singleton instance
        _instance = None
        
        def __new__(cls):
            if not cls._instance:
                cls._instance = super().__new__(cls)
            return cls._instance
        
        DATA = fileProperty(test_file)
        
        @DATA.callback
        def on_change(self, value):
            self.last_value = value

    # Test through singleton instance
    config = ClassConfig()
    config.DATA = {"version": 1}
    assert config.DATA == {"version": 1}
    assert os.path.exists(test_file)
    
    # Verify file content
    with open(test_file) as f:
        assert '{"version": 1}' in f.read()
    
    # Test modification
    config.DATA["updated"] = True
    config.DATA = config.DATA  # Trigger save
    assert config.DATA == {"version": 1, "updated": True}
    
    # Test callback
    assert hasattr(config, 'last_value')
    assert config.last_value == {"version": 1, "updated": True}
    
    # Test external changes
    with open(test_file, 'w') as f:
        f.write('{"external": "modification"}')
    
    # Should detect change on next access
    assert config.DATA == {"external": "modification"}

def test_class_instance_independence(tmp_path):
    """Test class property doesn't interfere with instance property"""
    class FileUser:
        CLASS_DATA = fileProperty(tmp_path / "class_data.json")
        
        def __init__(self):
            self.INSTANCE_DATA = fileProperty(tmp_path / "instance_data.json")

    # Set class property
    FileUser.CLASS_DATA = {"class": "value"}
    
    # Create instances
    user1 = FileUser()
    user2 = FileUser()
    
    # Set instance properties
    user1.INSTANCE_DATA = {"user1": "data"}
    user2.INSTANCE_DATA = {"user2": "data"}
    
    # Verify independence
    assert FileUser.CLASS_DATA == {"class": "value"}
    assert user1.INSTANCE_DATA == {"user1": "data"}
    assert user2.INSTANCE_DATA == {"user2": "data"}
    
    # Verify files exist
    assert os.path.exists(tmp_path / "class_data.json")
    assert os.path.exists(tmp_path / "instance_data.json")

def test_dynamic_class_path(tmp_path):
    """Test class property with dynamic path resolution"""
    class DynamicClass:
        _path = tmp_path / "dynamic.json"
        
        @classmethod
        def get_path(cls):
            return cls._path
        
        DATA = fileProperty(get_path)

    # Initial set
    DynamicClass.DATA = {"status": "active"}
    assert os.path.exists(DynamicClass._path)
    
    # Modify path
    new_path = tmp_path / "new_dynamic.json"
    DynamicClass._path = new_path
    
    # Should create new file
    DynamicClass.DATA = {"status": "moved"}
    assert os.path.exists(new_path)
    assert not os.path.exists(tmp_path / "dynamic.json")
