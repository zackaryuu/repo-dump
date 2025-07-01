from datetime import datetime, timedelta
import time
import re


def time_parse(time_str: str | float | int, relative: datetime | None = None):
    """
    Parse a time string or timestamp into a datetime object.

    Args:
        time_str: Input time as either:
            - A string with time units (e.g., "500ms", "1h", "30min")
            - A string parseable by dateparser
            - A cron expression string
            - A float timestamp
        relative: Base datetime reference (defaults to now if None)

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

    relative = relative or datetime.now()

    # Add early type validation
    if not isinstance(time_str, (str, int, float)):
        raise ValueError(f"Invalid input type: {type(time_str)}")

    if isinstance(time_str, str):
        time_str = time_str.strip()
        if time_str == "* * * * *" or time_str == "now":
            return relative

    try:
        return _parse_timestamp(time_str, relative)
    except ValueError:
        pass

    # Add type check before attempting unit parsing
    try:
        if isinstance(time_str, str):
            return _parse_units(time_str, relative)
    except ValueError:
        pass

    try:
        return _parse_combined(time_str, relative)
    except ValueError:
        pass

    try:
        return _parse_cron(time_str, relative)
    except ValueError:
        pass

    try:
        return _parse_natural(time_str)
    except ValueError as e:
        raise ValueError(f"Could not parse time string: {time_str}") from e


def _parse_combined(time_str: str, relative: datetime) -> datetime:
    if "+" not in time_str:
        raise ValueError("Not a combined format")

    parts = [part.strip() for part in time_str.split("+")]
    if len(parts) < 2:
        raise ValueError("Invalid combined format")

    base_time = time_parse(parts[0], relative=relative)
    total_duration = timedelta()

    for duration_part in parts[1:]:
        duration_time = time_parse(duration_part, relative=relative)
        duration = duration_time - relative
        total_duration += duration

    return base_time + total_duration


def _parse_timestamp(time_str: str | float | int, relative: datetime) -> datetime:
    # Handle absolute timestamps
    if isinstance(time_str, (int, float)):
        # Treat numbers >= 1e9 as UNIX timestamps (dates after 2001-09-09)
        if time_str >= 1e9:
            return datetime.fromtimestamp(float(time_str))
        
        # Treat smaller numbers as relative seconds
        return relative + timedelta(seconds=float(time_str))

    if isinstance(time_str, str) and time_str.count(".") <= 1 and time_str.replace(".", "").isdigit():
        numeric = float(time_str)
        if numeric >= 1e9:
            return datetime.fromtimestamp(numeric)
        return relative + timedelta(seconds=numeric)

    raise ValueError("Not a timestamp")


def _parse_units(time_str: str, relative: datetime) -> datetime:
    if not isinstance(time_str, str):
        raise ValueError("Units parser requires string input")
    
    time_units = {
        "ms": ("milliseconds", ["ms", "millisecond", "milliseconds"]),
        "s": ("seconds", ["s", "sec", "secs", "second", "seconds"]),
        "m": ("minutes", ["m", "min", "mins", "minute", "minutes"]),
        "h": ("hours", ["h", "hr", "hrs", "hour", "hours"]),
        "d": ("days", ["d", "day", "days"]),
        "w": ("weeks", ["w", "week", "weeks"]),
    }

    time_str = time_str.lower().strip()
    total_delta = timedelta()
    matches = re.findall(r"(\d+\.?\d*)\s*([a-z]+)", time_str)

    if not matches or "".join(f"{v}{u}" for v, u in matches) != time_str.replace(" ", ""):
        raise ValueError("Invalid unit format")

    for value_str, unit in matches:
        value = float(value_str)
        for base_unit, (delta_attr, variants) in time_units.items():
            if unit in variants:
                total_delta += timedelta(**{delta_attr: value})
                break
        else:
            raise ValueError(f"Unknown time unit: {unit}")

    return relative + total_delta


def _parse_cron(time_str: str, relative: datetime) -> datetime:
    from croniter import croniter
    cron = croniter(time_str, relative)
    return cron.get_next(datetime, relative)


def _parse_natural(time_str: str) -> datetime:
    import dateparser
    parsed = dateparser.parse(time_str)
    if not parsed:
        raise ValueError("Natural parsing failed")
    return parsed


def time_sleep(time_str: str | float | int):
    target_time = time_parse(time_str)
    sleep_duration = (target_time - datetime.now()).total_seconds()
    if sleep_duration > 0:
        time.sleep(sleep_duration)
