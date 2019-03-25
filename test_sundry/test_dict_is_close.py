
from copy import deepcopy

from sundry import dict_is_close


def test_dict_is_close():
    x = {'a': 1.0, 'b': 'some string', 3: {'d': 3.0}}
    y = deepcopy(x)

    # close
    y['a'] = 1.0000000001
    y[3]['d'] = 2.999999999

    assert(dict_is_close(x, y))

    # tighten up the requirement
    assert(not dict_is_close(x, y, 1e-12, 0.0))

    # loosen up the requirement
    y['a'] = 1.0001
    assert(dict_is_close(x, y, 1e-3, 0.0))

    y = deepcopy(x)
    y['a'] = 1.1  # too big of a difference
    assert(not dict_is_close(x, y))

    y = deepcopy(x)
    y['b'] = 'a different string'
    assert(not dict_is_close(x, y))

    y = deepcopy(x)
    y['b'] = 42  # different type
    assert(not dict_is_close(x, y))


if __name__ == "__main__":
    test_dict_is_close()
