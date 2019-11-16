
import math
from typing import TypeVar

DictIsCloseNumber = TypeVar('DictIsCloseNumber', int, float, complex)


class DictIsClose:
    def __init__(self, x: (dict, DictIsCloseNumber), y: (dict, DictIsCloseNumber), rel_tol: float = None, abs_tol: float = None):
        self._x = x
        self._y = y
        self._rel_tol = rel_tol
        self._abs_tol = abs_tol

    def is_close(self):
        if type(self._x) is float and type(self._y) is float:
            if self._rel_tol is None and self._abs_tol is None:
                # default tolerance
                return math.isclose(self._x, self._y)
            elif self._rel_tol is not None and self._abs_tol is not None:
                # user supplied tolerance
                return math.isclose(self._x, self._y, rel_tol=self._rel_tol, abs_tol=self._abs_tol)
            else:
                # require both
                raise ValueError(self._rel_tol, self._abs_tol)
        elif type(self._x) is dict and type(self._y) is dict:
            if self._x.keys() != self._y.keys():
                return False
            return all([DictIsClose(self._x[k], self._y[k], self._rel_tol, self._abs_tol).is_close() for k in self._x])
        else:
            return self._x == self._y


def dict_is_close(x: (dict, DictIsCloseNumber), y: (dict, DictIsCloseNumber), rel_tol: float = None, abs_tol: float = None):
    """

    Like doing x == y for a dict, except if there are floats then use math.isclose()

    :param x: input x

    :param y: input y

    :param rel_tol: relative tolerance to pass to math.close

    :param abs_tol: absolute tolerance to pass to math.close

    :return: True if dictionaries match and float values are close

    """
    _dict_is_close = DictIsClose(x, y, rel_tol, abs_tol)
    return _dict_is_close.is_close()
