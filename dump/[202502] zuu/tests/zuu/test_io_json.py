import pytest
from zuu.io import load_json, dump_json, load_json_w_encoding, dump_json_w_encoding


@pytest.fixture
def temp_json_file(tmp_path):
    return str(tmp_path /"test.json")

def test_basic_json_operations(temp_json_file):
    # Basic data
    test_data = {"hello": "world"}
    
    # Test dump and load
    dump_json(test_data, temp_json_file)
    loaded_data = load_json(temp_json_file)
    assert loaded_data == test_data

def test_json_with_non_ascii(temp_json_file):
    # Data with non-ASCII characters
    test_data = {
        "japanese": "こんにちは",
        "chinese": "你好",
        "emoji": "🌟🌍",
        "russian": "привет"
    }
    
    # Test with encoding-aware functions
    dump_json_w_encoding(test_data, temp_json_file)
    loaded_data = load_json_w_encoding(temp_json_file)
    assert loaded_data == test_data

def test_json_encoding_options(temp_json_file):
    test_data = {"special": "привет 🌟 こんにちは"}
    
    # Test with explicit encoding parameters
    dump_json_w_encoding(test_data, temp_json_file, encoding='utf-8')
    loaded_data = load_json_w_encoding(temp_json_file, encoding='utf-8')
    assert loaded_data == test_data

def test_json_ensure_ascii_behavior(temp_json_file):
    test_data = {"text": "こんにちは"}
    
    # Test with ensure_ascii=True (default in regular json)
    dump_json(test_data, temp_json_file)
    with open(temp_json_file, 'r', encoding='utf-8') as f:
        content = f.read()
        assert '\\u' in content  # Unicode escape sequences
    
    # Test with ensure_ascii=False (default in w_encoding version)
    dump_json_w_encoding(test_data, temp_json_file)
    with open(temp_json_file, 'r', encoding='utf-8') as f:
        content = f.read()
        assert 'こんにちは' in content  # Raw characters 