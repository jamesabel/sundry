
import math


def dict_is_close(x, y, rel_tol=None, abs_tol=None):
    """
    Like doing x = y, except if there are floats then use math.isclose()
    :param x:
    :param y:
    :param rel_tol:
    :param abs_tol:
    :return: True if dictionaries match
    """
    if type(x) is float and type(y) is float:
        if rel_tol is None and abs_tol is None:
            # default tolerance
            return math.isclose(x, y)
        elif rel_tol is not None and abs_tol is not None:
            # user supplied tolerance
            return math.isclose(x, y, rel_tol=rel_tol, abs_tol=abs_tol)
        else:
            raise ValueError
    elif type(x) is dict and type(y) is dict:
        if x.keys() != y.keys():
            return False
        return all([dict_is_close(x[k], y[k], rel_tol, abs_tol) for k in x])
    else:
        return x == y
