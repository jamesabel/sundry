from math import isinf, isnan, nan, inf

from typeguard import typechecked

rel_tol_default = 1e-09
abs_tol_default = 0.0


class Divergence:

    @typechecked(always=True)
    def __init__(self, label: (str, None), value: (float, int)):
        self.label = label
        self.value = value

    def __repr__(self):
        v = str(self.value)
        if self.label is None:
            s = v
        else:
            s = self.label + ":" + v
        return s


class Divergences:

    @typechecked(always=True)
    def __init__(self, max_divergences: int = 10):
        self.max_divergences = max_divergences
        self.divergences = []

    def __repr__(self):
        return self.divergences.__repr__()

    @typechecked(always=True)
    def add(self, divergence: Divergence):
        self.divergences.append(divergence)
        self.divergences.sort(key=lambda x: x.value)
        if len(self.divergences) > self.max_divergences:
            self.divergences.pop()

    def get(self):
        return self.divergences

    def max_value(self):
        mv = None
        if len(self.divergences) > 0:
            mv = self.divergences[-1].value
        return mv

    def max_label(self):
        ml = None
        if len(self.divergences) > 0:
            ml = self.divergences[-1].label
        return ml


@typechecked(always=True)
def _is_close(a: (float, int), b: (float, int), rel_tol: float, abs_tol: float, value_label: (str, None), divergences: Divergences):

    """
    similar to math.isclose() except is keeps track of which values have the greatest difference
    :param a: first input
    :param b: second input
    :param rel_tol: relative tolerance
    :param abs_tol: absolute tolerance
    :return:
    """

    # handle NaN, INF.  Matches math.isclose() .
    divergence_value = 0.0
    if isnan(a) or isnan(b):
        is_close_flag = False
        divergence_value = nan
    elif isinf(a) and isinf(b):
        is_close_flag = a == b  # handles both +INF and -INF
        if not is_close_flag:
            divergence_value = inf
    elif isinf(a) or isinf(b):
        is_close_flag = False  # only one or the other is (positive or negative) infinity
        divergence_value = inf
    elif isinf(rel_tol) or isinf(abs_tol):
        is_close_flag = True
    else:
        # is_close_flag is same as:
        # abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)
        divergence_value = abs(a - b) - max(rel_tol * max(abs(a), abs(b)), abs_tol)  # if > 0.0, values are *not* close
        is_close_flag = divergence_value <= 0.0

    if not is_close_flag and divergence_value is not None and (divergences.max_value() is None or divergence_value > divergences.max_value()):
        divergences.add(Divergence(value_label, divergence_value))

    return is_close_flag


@typechecked(always=True)
def _dict_is_close_max_value(x, y, rel_tol: (float, None), abs_tol: (float, None), parent_label: (str, None), divergences: Divergences):

    if rel_tol is None or isnan(rel_tol):
        rel_tol = rel_tol_default
    if abs_tol is None:
        abs_tol = abs_tol_default

    if (isinstance(x, float) or isinstance(x, int)) and (isinstance(y, float) or isinstance(y, int)):
        is_close_flag = _is_close(x, y, rel_tol, abs_tol, parent_label, divergences)
    elif isinstance(x, dict) and isinstance(y, dict):
        is_close_flags = []
        if set(x.keys()) == set(y.keys()):
            for k in x:
                # keys can be things other than strings, e.g. int
                str_k = str(k)
                if parent_label is None:
                    label = str_k
                else:
                    label = parent_label + "." + str_k
                is_close_flag = _dict_is_close_max_value(x[k], y[k], rel_tol, abs_tol, label, divergences)
                is_close_flags.append(is_close_flag)
        is_close_flag = all(is_close_flags)
    else:
        is_close_flag = x == y  # everything else that can be evaluated with == such as strings

    return is_close_flag


class DictIsClose:
    """
    Like doing x == y for a dict, except if there are floats then use math.isclose()
    """

    @typechecked(always=True)
    def __init__(self, x, y, rel_tol: float = None, abs_tol: float = None, divergences: Divergences = Divergences()):
        self._x = x
        self._y = y
        self._rel_tol = rel_tol
        self._abs_tol = abs_tol
        self.divergences = divergences
        self._is_close_flag = _dict_is_close_max_value(self._x, self._y, self._rel_tol, self._abs_tol, None, self.divergences)

    def __repr__(self):
        return self.divergences.__repr__()

    def is_close(self):
        return self._is_close_flag

    def get_max_divergence_value(self):
        return self.divergences.max_value()

    def get_max_divergence_label(self):
        return self.divergences.max_label()


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
