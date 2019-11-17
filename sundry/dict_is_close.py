from math import isinf, isnan

from typeguard import typechecked

rel_tol_default = 1e-09
abs_tol_default = 0.0


@typechecked(always=True)
def _is_close(a: (float, int), b: (float, int), rel_tol: float, abs_tol: float, value_label: str, max_divergence_label: str, max_divergence_value: (float, None)):

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
        # is_close_flag is same as:
        # abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)
        divergence = abs(a - b) - max(rel_tol * max(abs(a), abs(b)), abs_tol)  # if > 0.0, values are *not* close
        is_close_flag = divergence <= 0.0
        if not is_close_flag and (max_divergence_value is None or divergence > max_divergence_value):
            if len(max_divergence_label) > 0:
                max_divergence_label += "."
            max_divergence_label += value_label
            max_divergence_value = divergence

    return is_close_flag, max_divergence_label, max_divergence_value


@typechecked(always=True)
def _dict_is_close_max_value(x, y, rel_tol: (float, None), abs_tol: (float, None), value_label: str, max_divergence_label: str, max_divergence_value: (float, None)):

    if rel_tol is None or isnan(rel_tol):
        rel_tol = rel_tol_default
    if abs_tol is None:
        abs_tol = abs_tol_default

    if (isinstance(x, float) or isinstance(x, int)) and (isinstance(y, float) or isinstance(y, int)):
        is_close_flag, max_divergence_label, max_divergence_value = _is_close(x, y, rel_tol, abs_tol, value_label, max_divergence_label, max_divergence_value)
    elif isinstance(x, dict) and isinstance(y, dict):
        is_close_flags = []
        if set(x.keys()) == set(y.keys()):
            for k in x:
                # keys can be things other than strings, e.g. int
                is_close_flag, max_divergence_label, max_divergence_value = _dict_is_close_max_value(x[k], y[k], rel_tol, abs_tol, str(k), max_divergence_label, max_divergence_value)
                is_close_flags.append(is_close_flag)
        is_close_flag = all(is_close_flags)
    else:
        is_close_flag = x == y  # everything else that can be evaluated with == such as strings

    return is_close_flag, max_divergence_label, max_divergence_value


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
        self._is_close_flag, self._max_divergence_label, self._max_divergence_value = _dict_is_close_max_value(self._x, self._y, self._rel_tol, self._abs_tol, "", "", None)

    def is_close(self):
        return self._is_close_flag

    def get_max_divergence_value(self):
        return self._max_divergence_value

    def get_max_divergence_label(self):
        return self._max_divergence_label


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
