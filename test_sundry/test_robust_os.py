import os

from ismain import is_main

from sundry import mkdirs, rmdir


def test_robust_os():
    test_dir = os.path.join("temp", "test")
    mkdirs(test_dir, remove_first=True)
    assert os.path.exists(test_dir)
    rmdir(test_dir)
    assert not os.path.exists(test_dir)


if is_main():
    test_robust_os()
