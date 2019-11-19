import math

from ismain import is_main

from sundry import Divergence, Divergences


def test_dict_is_close_divergences():
    divergences = Divergences()
    assert(divergences.max_value() is None)
    assert(divergences.max_label() is None)
    divergences.add(Divergence("a", 1.0))
    assert math.isclose(divergences.max_value(), 1.0)
    divergences.add(Divergence("c", 3.0))
    assert math.isclose(divergences.max_value(), 3.0)
    divergences.add(Divergence("b", 2.0))
    assert math.isclose(divergences.max_value(), 3.0)
    assert divergences.max_label() == "c"
    assert str(divergences) == "[a:1.0, b:2.0, c:3.0]"  # test __repr__


if is_main():
    test_dict_is_close_divergences()
