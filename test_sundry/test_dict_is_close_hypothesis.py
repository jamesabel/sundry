import math
from pprint import pprint

from hypothesis import given
from hypothesis.strategies import floats
from ismain import is_main

from sundry import DictIsClose, Divergences

divergences = Divergences()


@given(floats(), floats(), floats(), floats())
def tst_dict_is_close_hypothesis(x, y, r, a):
    r = abs(r)
    a = abs(a)

    uut_result = DictIsClose(x, y, rel_tol=r, abs_tol=a, divergences=divergences).is_close()
    standard_library_result = math.isclose(x, y, rel_tol=r, abs_tol=a)
    if uut_result != standard_library_result:
        print("Error:")
        print(uut_result, standard_library_result)
        print(x, y, r, a)
    assert uut_result == standard_library_result


def test_dict_is_close_hypothesis():
    tst_dict_is_close_hypothesis()


if is_main():
    test_dict_is_close_hypothesis()
