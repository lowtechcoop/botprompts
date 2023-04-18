"""
This module is for stateless methods that assist with managing types, identifying numbers
"""

TRUE_BOOLS = [
    "true",
    "yes",
    "1",
]

FALSE_BOOLS = [
    "false",
    "no",
    "0",
]

def is_numeric(n: str) -> bool:
    """
    Attempts to check if a string is numeric
    """

    try:
        return True if float(n) else float(n).is_integer()
    except ValueError:
        return False
    except TypeError:
        return False


def is_integer(n: str) -> bool:
    """
    Attempts to check if a string is an integer
    """
    try:
        float(n)
    except ValueError:
        return False
    else:
        return float(n).is_integer()


def is_boolean(n:str) -> bool:
    """
    Attempts to check if a string can be a boolean
    """

    try:
        if n.lower() in [
            "true",
            "false",
            "yes",
            "no",
        ]:
            return True
    except ValueError:
        return False
    else:
        return False

def parse_type(n: str) -> str | int | float | bool:
    """
    Reads an input string and returns the same value as a string, integer, float, or boolean
    """

    if is_numeric(n):
        if is_integer(n):
            return int(n)
        else:
            return float(n)
    else:

        if is_boolean(n):
            if n.lower() in TRUE_BOOLS:
                return True
            elif n.lower() in FALSE_BOOLS:
                return False

        return n
