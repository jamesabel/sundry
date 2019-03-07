
from sundry import get_func_name, get_line_number


def test_get_func_name():
    assert(get_func_name() == "test_get_func_name")
    assert(get_line_number() == 7)
    return get_func_name(), get_line_number()


if __name__ == "__main__":
    print(test_get_func_name())
