from dataclasses import dataclass, asdict

import pytest
from ismain import is_main

from sundry import dataclass_chain


def test_dataclass_chain():

    @dataclass
    class C:
        w: int = None
        x: str = None
        y: str = None

    @dataclass
    class D(C):
        z: int = None

    a = C(x="a", w=2)
    b = C(x="b", y="c", w=2)
    c = D(z=4)

    expected = {"w": 2, "x": "a", "y": "c", "z": 4}

    no_exception_results = dataclass_chain(D, a, b, c, raise_exception=False)
    assert asdict(no_exception_results) == expected

    with pytest.raises(ValueError):
        dataclass_chain(D, a, b, c)


if is_main():
    test_dataclass_chain()
