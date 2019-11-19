import math

from ismain import is_main

from sundry import ValueDivergence, ValueDivergences


def test_dict_is_close_divergences():
    divergences = ValueDivergences()
    assert(divergences.max_label() is None)
    divergences.add(ValueDivergence("a", 1.0))
    assert math.isclose(divergences.max_value(), 1.0)
    divergences.add(ValueDivergence("c", 3.0))
    assert math.isclose(divergences.max_value(), 3.0)
    divergences.add(ValueDivergence("b", 2.0))
    assert math.isclose(divergences.max_value(), 3.0)
    assert divergences.max_label() == "c"
    assert str(divergences) == "[a:1.0, b:2.0, c:3.0]"  # test __repr__


if is_main():
    test_dict_is_close_divergences()
