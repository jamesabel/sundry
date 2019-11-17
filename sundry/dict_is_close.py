from math import isinf, isnan

from typeguard import typechecked

rel_tol_default = 1e-09
abs_tol_default = 0.0


@typechecked(always=True)
def _is_close(a: float, b: float, rel_tol: float, abs_tol: float):

    """
    similar to math.isclose() except is keeps track of which values have the greatest difference
    :param a: first input
    :param b: second input
    :param rel_tol: relative tolerance
    :param abs_tol: absolute tolerance
    :return:
    """

    # handle NaN, INF.  Matches math.isclose() .
    if isnan(a) or isnan(b):
        is_close_flag = False
    elif isinf(a) and isinf(b):
        is_close_flag = a == b  # handles both +INF and -INF
    elif isinf(a) or isinf(b):
        is_close_flag = False  # only one or the other is (positive or negative) infinity
    elif isinf(rel_tol) or isinf(abs_tol):
        is_close_flag = True
    else:
        is_close_flag = abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

    return is_close_flag


@typechecked(always=True)
def _dict_is_close_max_value(x, y, rel_tol: (float, None) = rel_tol_default, abs_tol: (float, None) = abs_tol_default, max_difference_label=None, max_difference_value: float = None):

    if rel_tol is None or isnan(rel_tol):
        rel_tol = rel_tol_default
    if abs_tol is None:
        abs_tol = abs_tol_default

    if isinstance(x, float) and isinstance(y, float):
        is_close_flag = _is_close(x, y, rel_tol, abs_tol)
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

    @typechecked(always=True)
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


@typechecked(always=True)
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
