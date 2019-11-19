from copy import deepcopy
from pprint import pprint

from sundry import dict_is_close, DictIsClose


def test_dict_is_close():
    x = {"a": 1.0, "b": "some string", 3: {"d": 3.0}}
    y = deepcopy(x)

    # close
    y["a"] = 1.0000000001
    y[3]["d"] = 2.999999999

    assert dict_is_close(x, y)
    dic = DictIsClose(x, y)
    assert dic.is_close()
    assert len(dic.divergences) == 0
    print(dic)

    # tighten up the requirement
    assert not dict_is_close(x, y, 1e-12, 0.0)

    # loosen up the requirement
    y["a"] = 1.0001
    assert dict_is_close(x, y, 1e-3, 0.0)

    y = deepcopy(x)
    y["a"] = 1.1  # too big of a difference
    assert not dict_is_close(x, y)

    # test for the divergence label and value
    dic = DictIsClose(x, y)
    assert not dic.is_close()
    assert dic.divergences.max_label() == "a"
    assert dic.divergences.max_value() > 0.0
    assert len(dic.divergences) > 0
    pprint(dic)

    y = deepcopy(x)
    y["b"] = "a different string"
    assert not dict_is_close(x, y)
    dic = DictIsClose(x, y)
    # pprint(dic)

    y = deepcopy(x)
    y["b"] = 42  # different type
    assert not dict_is_close(x, y)


if __name__ == "__main__":
    test_dict_is_close()
