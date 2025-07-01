from string import Formatter as _Formatter


def is_fstring(string: str):
    """
    Check if a given string is a formatted string literal (f-string).

    Args:
        string (str): The string to be checked.

    Returns:
        bool: True if the string is a formatted string literal, False otherwise.
    """
    if not isinstance(string, str):
        return False
    try:
        _Formatter().parse(string)
        return True
    except ValueError:
        return False


def extract_fstring_keys(string: str):
    """
    Extracts the keys used in a formatted string literal (f-string).

    Args:
        string (str): The formatted string literal.

    Returns:
        list: A list of keys used in the f-string.

    This function takes a formatted string literal (f-string) as input and extracts the keys used in it. It checks if the input is a string and if not, it returns an empty list. If the input is a string, it uses the `Formatter().parse()` method to parse the string and extract the keys. It then returns a list of keys used in the f-string. If any error occurs during the parsing, it returns an empty list.

    Example:
        >>> extract_fstring_keys("Hello, {name}!")
        ['name']
        >>> extract_fstring_keys("The answer is {answer}.")
        ['answer']
        >>> extract_fstring_keys("This is not an f-string.")
        []
    """
    if not isinstance(string, str):
        return []
    try:
        return [x[1] for x in _Formatter().parse(string) if x[1] is not None]
    except ValueError:
        return []


def rreplace(s: str, old: str, new: str, occurrence):
    """
    Replaces the last occurrence of a substring in a string with a new substring.

    Args:
        s (str): The input string.
        old (str): The substring to be replaced.
        new (str): The new substring to replace the old substring.
        occurrence (int): The number of occurrences of the old substring to replace.

    Returns:
        str: The modified string with the last occurrence of the old substring replaced by the new substring.

    Raises:
        None

    Example:
        >>> rreplace("Hello, world!", "world", "codeium", 1)
        'Hello, codeium!'
    """
    if occurrence <= 0:
        return s

    parts = s.rsplit(old, occurrence)
    return new.join(parts)
