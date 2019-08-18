
from sundry import is_main

from .test import *


def test_is_main():
    assert (not is_main())


if __name__ == "__main__":
    assert (is_main())
