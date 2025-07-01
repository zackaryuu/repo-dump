from datetime import datetime
import time


def time_parse(time_str: str | float | int):
    """
    Parse a time string or timestamp into a datetime object.

    Args:
        time_str: Input time as either:
            - A string with time units (e.g., "500ms", "1h", "30min")
            - A string parseable by dateparser
            - A cron expression string
            - A float timestamp

    Supported time units:
        - ms, milliseconds
        - s, sec, seconds
        - m, min, minutes
        - h, hr, hrs, hours
        - d, days
        - w, weeks

    Returns:
        datetime: The parsed datetime object
        
    Raises:
        ImportError: If required modules dateparser or croniter are not installed
        ValueError: If the time string cannot be parsed
    """
    

    from datetime import datetime, timedelta
    import re

    if isinstance(time_str, str) and time_str == "* * * * *":
        return datetime.now()
    
    if isinstance(time_str, str) and time_str == "now":
        return datetime.now()

    # Try parsing combined date + duration format
    if isinstance(time_str, str) and '+' in time_str:
        parts = [part.strip() for part in time_str.split('+')]
        if len(parts) < 2:
            raise ValueError("Invalid combined format")
        
        try:
            # Parse base time from first part
            base_time = time_parse(parts[0])
            
            # Calculate total duration from subsequent parts
            total_duration = timedelta()
            for duration_part in parts[1:]:
                duration_time = time_parse(duration_part)
                duration = duration_time - datetime.now()
                total_duration += duration
            
            return base_time + total_duration
        except ValueError:
            pass

    # Handle numeric timestamps
    if isinstance(time_str, (int, float)) or (
        isinstance(time_str, str)
        and time_str.count(".") <= 1
        and time_str.replace(".", "").isdigit()
    ):
        return datetime.now() + timedelta(seconds=float(time_str))

    # Handle string inputs
    if isinstance(time_str, str):
        # Try parsing as time units (supports multiple units now)
        time_units = {
            'ms': ('milliseconds', ['ms', 'millisecond', 'milliseconds']),
            's': ('seconds', ['s', 'sec', 'secs', 'second', 'seconds']),
            'm': ('minutes', ['m', 'min', 'mins', 'minute', 'minutes']),
            'h': ('hours', ['h', 'hr', 'hrs', 'hour', 'hours']),
            'd': ('days', ['d', 'day', 'days']),
            'w': ('weeks', ['w', 'week', 'weeks'])
        }

        time_str = time_str.lower().strip()
        total_delta = timedelta()
        valid_units = True
        
        # Find all (value, unit) pairs in the string
        matches = re.findall(r'(\d+\.?\d*)\s*([a-z]+)', time_str)
        if matches:
            # Verify entire string is consumed by matches
            reconstructed = ''.join(f"{v}{u}" for v, u in matches)
            if reconstructed.replace(' ', '') != time_str.replace(' ', ''):
                valid_units = False
            else:
                for value_str, unit in matches:
                    try:
                        value = float(value_str)
                        matched = False
                        for base_unit, (delta_attr, variants) in time_units.items():
                            if unit in variants:
                                total_delta += timedelta(**{delta_attr: value})
                                matched = True
                                break
                        if not matched:
                            valid_units = False
                            break
                    except ValueError:
                        valid_units = False
                        break
                
                if valid_units:
                    return datetime.now() + total_delta

        # Try parsing as cron expression (fixed return type)
        try:
            from croniter import croniter
            base = datetime.now()
            cron = croniter(time_str, base)
            next_time = cron.get_next(datetime, datetime.now())
            return next_time
        except (ImportError, TypeError, ValueError):
            pass

        # Try parsing with dateparser
        try:
            import dateparser
        except ImportError:
            raise ImportError("dateparser module is required for natural language date parsing")
            
        parsed = dateparser.parse(time_str)
        if parsed:
            return parsed

    raise ValueError(f"Could not parse time string: {time_str}")

def time_sleep(time_str: str | float | int):
    target_time = time_parse(time_str)
    sleep_duration = (target_time - datetime.now()).total_seconds()
    if sleep_duration > 0:
        time.sleep(sleep_duration)
