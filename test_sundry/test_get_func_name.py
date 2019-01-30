
from sundry import get_func_name


def test_get_func_name():
    assert(get_func_name() == "test_get_func_name")
    return get_func_name()


if __name__ == "__main__":
    print(test_get_func_name())
