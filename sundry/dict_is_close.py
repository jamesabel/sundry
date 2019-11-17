import math


def _dict_is_close_max_value(x, y, rel_tol: float = None, abs_tol: float = None, max_difference_label=None, max_difference_value: float = None):

    if isinstance(x, float) and isinstance(y, float):
        if rel_tol is None and abs_tol is None:
            # default tolerance
            is_close_flag = math.isclose(x, y)
        elif rel_tol is not None and abs_tol is not None:
            # user supplied tolerance
            is_close_flag = math.isclose(x, y, rel_tol=rel_tol, abs_tol=abs_tol)
        else:
            # require both
            raise ValueError(rel_tol, abs_tol)
    elif isinstance(x, dict) and isinstance(y, dict):
        is_close_flag = False
        if set(x.keys()) == set(y.keys()):
            is_close_flag = all([DictIsClose(x[k], y[k], rel_tol, abs_tol).is_close() for k in x])
    else:
        is_close_flag = x == y

    return is_close_flag, max_difference_label, max_difference_value


class DictIsClose:
    """
    Like doing x == y for a dict, except if there are floats then use math.isclose()
    """

    def __init__(self, x, y, rel_tol: float = None, abs_tol: float = None):
        self._x = x
        self._y = y
        self._rel_tol = rel_tol
        self._abs_tol = abs_tol
        self._max_difference_label = None
        self._max_difference_value = None

    def is_close(self):
        is_close_flag, self._max_difference_label, self._max_difference_value = _dict_is_close_max_value(self._x, self._y, self._rel_tol, self._abs_tol)
        return is_close_flag


def dict_is_close(x, y, rel_tol: float = None, abs_tol: float = None):
    """

    Like doing x == y for a dict, except if there are floats then use math.isclose()

    :param x: input x
    :param y: input y
    :param rel_tol: relative tolerance to pass to math.close
    :param abs_tol: absolute tolerance to pass to math.close
    :return: True if dictionaries match and float values are close

    """
    return DictIsClose(x, y, rel_tol, abs_tol).is_close()
