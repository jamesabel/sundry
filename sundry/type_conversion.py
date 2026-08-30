from decimal import Decimal

_true_strings = ("y", "yes", "t", "true", "on", "1")
_false_strings = ("n", "no", "f", "false", "off", "0")


def _strtobool(value: str) -> bool:
    """
    Same semantics as the former distutils.util.strtobool (distutils was removed in Python 3.12).
    """
    lowered = value.lower()
    if lowered in _true_strings:
        return True
    if lowered in _false_strings:
        return False
    raise ValueError(f"invalid truth value {value!r}")


def to_bool(value):
    """
    performs a casting of a multitude of values to bool.
    i.e. "true", "TRUE", "y", "Yes", "on", "1", 1, "false", "FALSE", "n", "No", "off", "0", 0, etc.
    :param value: input value
    :return: boolean value of original string
    """

    if type(value) == bool:
        new_bool = value
    elif value is None:
        new_bool = None
    elif type(value) == int and 0 <= value <= 1:
        new_bool = bool(value)
    elif type(value) == Decimal and (value == Decimal(0) or value == Decimal(1)):
        new_bool = bool(value)
    elif type(value) == str:
        if value.lower() == "none" or value.lower() == "null":
            new_bool = None
        else:
            new_bool = _strtobool(value)
    else:
        raise ValueError(value)

    return new_bool
