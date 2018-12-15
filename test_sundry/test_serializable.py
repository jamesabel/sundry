
from decimal import Decimal
from enum import Enum

from sundry import make_serializable


class TstClass(Enum):
    a = 1
    b = 2


def test_make_serializable():
    values = {'d': Decimal(1.0),
              's': 's',
              'bool': True,
              'a': TstClass.a,
              'b': TstClass.b}
    serial_values = make_serializable(values)
    assert(serial_values['d'] == 1.0)
    assert(serial_values['s'] == 's')
    assert(serial_values['bool'] is True)
    assert(serial_values['a'] == 1)
    assert(serial_values['b'] == 2)
