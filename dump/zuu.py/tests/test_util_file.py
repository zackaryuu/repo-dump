import os
import pytest
import stat
from zuu.util_file import (
    read_first_and_last_byte,
    iter_by_chunk,
    determine_file_type,
    serialize,
    deserialize,
    load,
    touch,
    path_match,
    save,
)

@pytest.fixture(scope="module", autouse=True)
def setup_teardown():
    test_dir = "test_files"
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
    yield
    # Retry cleanup for Windows file locks
    for f in os.listdir(test_dir):
        file_path = os.path.join(test_dir, f)
        try:
            os.remove(file_path)
        except PermissionError:
            os.chmod(file_path, stat.S_IWRITE)
            os.remove(file_path)
    os.rmdir(test_dir)

@pytest.fixture
def temp_file():
    file_path = os.path.join("test_files", "test_file.txt")
    with open(file_path, "w") as f:
        f.write("test content")
    return file_path

def test_read_first_and_last_byte():
    # Test empty file
    empty_file = os.path.join("test_files", "empty.dat")
    with open(empty_file, "wb") as f:  # Use binary mode
        pass  # Create empty file
    first, last = read_first_and_last_byte(empty_file)
    assert first == b"" and last == b""
    os.remove(empty_file)

    # Test single byte file
    single_byte = os.path.join("test_files", "single.dat")
    with open(single_byte, "wb") as f:
        f.write(b"A")
    first, last = read_first_and_last_byte(single_byte)
    assert first == b"A" and last == b"A"
    os.remove(single_byte)

    # Test multi-byte file
    multi_byte = os.path.join("test_files", "multi.dat")
    with open(multi_byte, "wb") as f:
        f.write(b"ABCD")
    first, last = read_first_and_last_byte(multi_byte)
    assert first == b"A" and last == b"D"
    os.remove(multi_byte)

def test_iter_by_chunk():
    test_content = b"1234567890"
    file_path = os.path.join("test_files", "chunk_test.dat")
    
    # Create test file with explicit close
    with open(file_path, "wb") as f:
        f.write(test_content)
    
    # Test chunk reading
    chunks = list(iter_by_chunk(file_path, 3))
    assert chunks == [b"123", b"456", b"789", b"0"]
    
    # Clean up
    os.remove(file_path)

def test_determine_file_type():
    assert determine_file_type("test.json") == "json"
    assert determine_file_type("config.yml") == "yaml"
    assert determine_file_type("data.toml") == "toml"
    assert determine_file_type("file.xml") == "xml"
    assert determine_file_type("table.csv") == "csv"
    assert determine_file_type("model.pkl") == "pickle"
    assert determine_file_type("unknown.xyz") == "plain"

def test_serialize_deserialize_roundtrip():
    test_data = {"key": "value"}
    
    # Test JSON
    serialized = serialize(test_data, "json")
    assert deserialize(serialized, "json") == test_data
    
    # Test YAML
    serialized = serialize(test_data, "yaml")
    assert deserialize(serialized, "yaml") == test_data

def test_touch():
    test_path = os.path.join("test_files", "new_file.txt")
    touch(test_path)
    assert os.path.exists(test_path)
    
    # Test initial data
    test_with_data = os.path.join("test_files", "data_file.txt")
    touch(test_with_data, initial_data="content")
    assert open(test_with_data).read() == "content"
    os.remove(test_with_data)
    os.remove(test_path)

def test_file_not_found():
    with pytest.raises(FileNotFoundError):
        load("non_existent_file.txt")

def test_unsupported_file_type():
    with pytest.raises(ValueError):
        serialize({}, "invalid_type")
    with pytest.raises(ValueError):
        deserialize("data", "invalid_type")

@pytest.fixture
def sample_dir(tmp_path):
    # Create directory structure:
    # tmp_path/
    # ├── file1.txt
    # ├── subdir1/
    # │   ├── file2.txt
    # │   └── subsubdir1/
    # │       └── file3.txt
    # ├── subdir2/
    # │   └── file4.md
    # └── image.png
    
    (tmp_path / "file1.txt").touch()
    (tmp_path / "image.png").touch()
    
    subdir1 = tmp_path / "subdir1"
    subdir1.mkdir()
    (subdir1 / "file2.txt").touch()
    (subdir1 / "subsubdir1").mkdir()
    (subdir1 / "subsubdir1" / "file3.txt").touch()
    
    subdir2 = tmp_path / "subdir2"
    subdir2.mkdir()
    (subdir2 / "file4.md").touch()
    
    return tmp_path

def test_depth_0(sample_dir):
    """Depth 0: Only matches root directory itself"""
    result = path_match([str(sample_dir)], ["*"], depth=0)
    assert result == [str(sample_dir)]

def test_depth_1_files(sample_dir):
    """Depth 1: Root's immediate children (files and dirs)"""
    result = path_match([str(sample_dir)], ["*.txt"], depth=1)
    expected = [
        str(sample_dir / "file1.txt"),
    ]
    assert sorted(result) == sorted(expected)

def test_depth_3_full(sample_dir):
    """Depth 3: All descendants up to grandchildren level"""
    result = path_match([str(sample_dir)], ["*.txt"], depth=3)
    expected = [
        str(sample_dir / "file1.txt"),
        str(sample_dir / "subdir1" / "file2.txt"),
        str(sample_dir / "subdir1" / "subsubdir1" / "file3.txt")
    ]
    assert sorted(result) == sorted(expected)

def test_depth_unlimited(sample_dir):
    """Unlimited depth: All descendants"""
    # Create the additional file within THIS test
    another_dir = sample_dir / "another"
    another_dir.mkdir()
    file5 = another_dir / "file5.txt"
    file5.touch()
    
    result = path_match([str(sample_dir)], ["*.txt"], depth=-1)
    expected = [
        str(sample_dir / "file1.txt"),
        str(sample_dir / "subdir1" / "file2.txt"),
        str(sample_dir / "subdir1" / "subsubdir1" / "file3.txt"),
        str(file5)  # Now created in this test
    ]
    assert sorted(result) == sorted(expected)

def test_mixed_pattern_types(sample_dir):
    # Test combination of path and basename patterns
    result = path_match([str(sample_dir)], ["subdir2/*.md", "image.*"], depth=-1)
    expected = [
        str(sample_dir / "image.png"),
        str(sample_dir / "subdir2" / "file4.md")
    ]
    assert sorted(result) == sorted(expected)

def test_multiple_root_directories(sample_dir):
    # Test with multiple input paths
    another_dir = sample_dir / "another"
    another_dir.mkdir()
    (another_dir / "file5.txt").touch()
    
    result = path_match([str(sample_dir), str(another_dir)], ["file*.txt"], depth=1)
    expected = [
        str(sample_dir / "file1.txt"),
        str(another_dir / "file5.txt")
    ]
    assert sorted(result) == sorted(expected) 

def test_imaginary_paths():
    pathes = [
        "x/y/z",
        "x/y/z/a",
        "x/y/z/b",
        "x/y/z/c",
        "x/y/z/d",
        "x/y/z/e",
        "x/y/z/f/a.txt",
        "x/y/z/f/b.txt",
        "x/y/z/f/g/c.txt",
    ]

    matches = [
        "g/*.txt"
    ]

    result = path_match(pathes, matches, depth=0)
    assert result == [
        "x/y/z/f/g/c.txt"
    ]

@pytest.fixture
def temp_json_file(tmp_path):
    return str(tmp_path / "test.json")

def test_basic_json_operations(temp_json_file):
    test_data = {"hello": "world"}
    
    # Use save/load instead of serialize/deserialize
    save(test_data, temp_json_file, file_type='json')
    loaded_data = load(temp_json_file)
    assert loaded_data == test_data

def test_json_with_non_ascii(temp_json_file):
    test_data = {
        "japanese": "こんにちは",
        "chinese": "你好",
        "emoji": "🌟🌍",
        "russian": "привет"
    }
    
    save(test_data, temp_json_file, file_type='json', encoding='utf-8')
    loaded_data = load(temp_json_file, encoding='utf-8')
    assert loaded_data == test_data

def test_json_encoding_options(temp_json_file):
    test_data = {"special": "привет 🌟 こんにちは"}
    
    save(test_data, temp_json_file, file_type='json', encoding='utf-8')
    loaded_data = load(temp_json_file, encoding='utf-8')
    assert loaded_data == test_data

def test_json_ensure_ascii_behavior(temp_json_file):
    test_data = {"text": "こんにちは"}
    
    # Test with ensure_ascii=True
    save(test_data, temp_json_file, file_type='json', ensure_ascii=True)
    with open(temp_json_file, 'r', encoding='utf-8') as f:
        content = f.read()
        assert '\\u' in content  # Unicode escapes
    
    # Test with ensure_ascii=False
    save(test_data, temp_json_file, file_type='json', ensure_ascii=False)
    with open(temp_json_file, 'r', encoding='utf-8') as f:
        content = f.read()
        assert 'こんにちは' in content  # Raw characters

