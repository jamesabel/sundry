import math

from hypothesis import given
from hypothesis.strategies import floats
from ismain import is_main

from sundry import dict_is_close


@given(floats(), floats(), floats(), floats())
def tst_dict_is_close_hypothesis(x, y, r, a):
    r = abs(r)
    a = abs(a)
    assert dict_is_close(x, y,  rel_tol=r, abs_tol=a) == math.isclose(x, y, rel_tol=r, abs_tol=a)


def test_dict_is_close_hypothesis():
    tst_dict_is_close_hypothesis()


if is_main():
    test_dict_is_close_hypothesis()
