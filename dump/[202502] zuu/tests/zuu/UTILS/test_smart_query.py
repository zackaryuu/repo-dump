from zuu.UTILS.smart_query import QueryObj as query
import pytest 

class TestParse:
    @staticmethod
    def test_parse_simple_query():
        q = query.parse("name contains test")
        assert q.query == "CONTAINS(name, \"test\")"
        assert q.stats["isCompound"] is False

    @staticmethod
    def test_parse_compound_query():
        q = query.parse("name contains test and id is 1")
        assert q.stats["isCompound"] is True

    @staticmethod
    def test_parse_logical_operators():
        # Test && operator
        q1 = query.parse("name contains test && id is 1")
        q2 = query.parse("name contains test and id is 1") 
        assert q1.query == q2.query

        # Test || operator
        q1 = query.parse("name contains test || id is 1")
        q2 = query.parse("name contains test or id is 1")
        assert q1.query == q2.query

        # Test ! operator
        q1 = query.parse("!name contains test")
        q2 = query.parse("not name contains test")
        assert q1.query == q2.query

    @staticmethod
    def test_parse_nlp_patterns():
        test_cases = [
            ("name contains test", "CONTAINS(name, \"test\")"),
            ("name is test", "name == \"test\""),
            ("name startswith test", "name.startswith(\"test\")"),
            ("name endswith test", "name.endswith(\"test\")"),
            ("name pattern of test", "REGEX(name, \"test\")")
        ]
        
        for input_q, expected in test_cases:
            q = query.parse(input_q)
            assert q.query == expected

    @staticmethod
    def test_nested_logical_expressions():
        q = query.parse("(name contains test && id is 1) || title startswith demo")
        assert q.stats["isCompound"] is True


class TestValidate:
    @staticmethod
    @pytest.mark.parametrize("query_str, data, expected", [
        # Basic equality tests
        ("name is John", {"name": "John"}, True),
        ("name is John", {"name": "Alice"}, False),
        
        # Contains tests
        ("bio contains engineer", {"bio": "software engineer"}, True),
        ("bio contains engineer", {"bio": "doctor"}, False),
        
        # Regex tests
        ("name pattern of J*", {"name": "John"}, True),
        ("name pattern of J*", {"name": "Mike"}, False),
        
        # Default key regex
        ("J.*", {"name": "John"}, True),  # Uses first key as default
        ("J.*", {"name": "Alice"}, False),
        
        # Compound queries
        ("name is John and age is 30", {"name": "John", "age": 30}, True),
        ("name is John and age is 30", {"name": "John", "age": 25}, False),
        ("name is John or age is 30", {"name": "Alice", "age": 30}, True),
        ("name is John or age is 30", {"name": "Alice", "age": 25}, False),
        
        # Negation tests
        ("not name is John", {"name": "Alice"}, True),
        ("not name is John", {"name": "John"}, False),
        
        # Case sensitivity
        ("name is john", {"name": "John"}, False),
        ("name pattern of j*", {"name": "John"}, False),
        
        # Missing key handling
        ("name is John", {"age": 30}, False),
        ("age > 25", {"name": "John"}, False),
    ])
    def test_validate_queries(query_str, data, expected):
        query_obj = query.parse(query_str)
        assert query_obj.validate(data) == expected

    @staticmethod
    def test_nested_compound_validation():
        query_obj = query.parse("(name contains Jo or age < 30) and not title contains Manager")
        

        # Should match (True OR True) AND NOT True -> (True) AND False -> False
        assert not query_obj.validate({
            "name": "Jolyne",
            "age": 25,
            "title": "Project Manager"
        })
        
        # Should match (True OR False) AND NOT False -> True AND True -> True
        assert query_obj.validate({
            "name": "Jo",
            "age": 35,
            "title": "Developer"
        }) 