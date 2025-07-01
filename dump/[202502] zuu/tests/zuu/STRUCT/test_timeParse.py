import pytest
from datetime import datetime, timedelta
from unittest.mock import patch
from src.zuu.STRUCT.time_parse import time_parse
import time

class TestTimeParse:
    def test_numeric_timestamps(self):
        # Test integer timestamp
        ts = int(time.time())
        result = time_parse(ts)
        assert isinstance(result, datetime)
        assert result == datetime.fromtimestamp(ts)

        # Test float timestamp
        result = time_parse(float(ts))
        assert result == datetime.fromtimestamp(ts)

        # Test string timestamp
        result = time_parse(str(ts))
        assert result == datetime.fromtimestamp(ts)

    def test_time_units(self):
        now = datetime.now()
        tolerance = timedelta(milliseconds=50)

        # Test milliseconds
        result = time_parse("500ms")
        assert isinstance(result, datetime)
        assert abs((result - now) - timedelta(milliseconds=500)) < tolerance

        # Test complex duration
        result = time_parse("1h30m")
        expected = now + timedelta(hours=1, minutes=30)
        assert abs(result - expected) < tolerance

    def test_cron_expressions(self):
        now = datetime.now() + timedelta(hours=1)

        result = time_parse("0 * * * *")
        assert isinstance(result, datetime)
        assert abs((result - now).total_seconds()) < 3600  # Assert difference is less than 1 hour

    @patch('dateparser.parse')
    def test_natural_language(self, mock_parse):
        # Mock dateparser response
        expected = datetime(2023, 12, 25, 12, 0)
        mock_parse.return_value = expected

        result = time_parse("next christmas")
        assert isinstance(result, datetime)
        assert result == expected

    def test_edge_cases(self):
        # Test empty string
        with pytest.raises(ValueError):
            time_parse("")

        # Test invalid type
        with pytest.raises(ValueError):
            time_parse(["invalid"])

        # Test combined formats
        result = time_parse("2023-01-01 12:00 + 30min")
        assert isinstance(result, datetime)
        assert result == datetime(2023, 1, 1, 12, 30)

    def test_error_handling(self):
        # Test missing dateparser
        with patch.dict('sys.modules', {'dateparser': None}):
            with pytest.raises(ImportError):
                time_parse("tomorrow")

    def test_time_elapsed(self):
        result = time_parse("100ms")
        assert result - (datetime.now() + timedelta(milliseconds=100)) < timedelta(milliseconds=50)

        result = time_parse("100s")
        assert result - (datetime.now() + timedelta(seconds=100)) < timedelta(seconds=1)

        result = time_parse("100m")
        assert result - (datetime.now() + timedelta(minutes=100)) < timedelta(seconds=1)
        
        result = time_parse("100h")
        assert result - (datetime.now() + timedelta(hours=100)) < timedelta(seconds=1)

        result = time_parse("100d")
        assert result - (datetime.now() + timedelta(days=100)) < timedelta(seconds=1)

        result = time_parse("in 10 minutes")
        assert result - (datetime.now() + timedelta(minutes=10)) < timedelta(seconds=1)

        result = time_parse("in 10 hours")
        assert result - (datetime.now() + timedelta(hours=10)) < timedelta(seconds=1)

        result = time_parse("in 10 days")
        assert result - (datetime.now() + timedelta(days=10)) < timedelta(seconds=1)

    def test_return_type_guarantee(self):
        # Verify all valid inputs return datetime
        test_cases = [
            1672531200,  # timestamp
            "1672531200",  # string timestamp
            "1h30m",      # time units
            "next week",  # natural language
            "* * * * *",  # cron expression
        ]

        for case in test_cases:
            result = time_parse(case)
            assert isinstance(result, datetime), f"Failed for {case}"