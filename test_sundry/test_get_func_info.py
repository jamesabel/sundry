import os
from sundry import get_func_name, get_line_number, get_file_name, get_file_path


def test_get_func_name():
    assert(get_func_name() == "test_get_func_name")
    assert(get_line_number() == 7)
    assert(get_file_name() == "test_get_func_info.py")

    # sometimes we split on /, other times \
    file_path = get_file_path().split('/')[-3:]
    if len(file_path) == 1:
        file_path = get_file_path().split(os.sep)[-3:]

    assert(file_path == ["sundry", "test_sundry", "test_get_func_info.py"])

    return get_func_name(), get_line_number(), get_file_name(), get_file_path()


if __name__ == "__main__":
    print(test_get_func_name())
