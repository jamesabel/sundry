from decimal import Decimal
import distutils.util


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
        if value.lower() == 'none' or value.lower() == 'null':
            new_bool = None
        else:
            # strtobool actually returns an int
            new_bool = bool(distutils.util.strtobool(value))
    else:
        raise ValueError(value)

    return new_bool
