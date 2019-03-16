
import sys
import decimal
from collections import OrderedDict, defaultdict
from pprint import pprint
import math

from sundry import dict_to_dynamodb


def test_dict_to_dynamodb():

    od = OrderedDict()
    od['a'] = 1
    od['b'] = 2

    dd = defaultdict(int)
    dd[1] = 2

    sample_input = {
        'sample1': 'Test Data',
        'sample2': 2.0,
        'sample3': True,
        'sample4': int(1),
        'sample5': None,
        'sample6': {
            'test': True
        },
        'sample7': [
            "Hello",
            "World"
        ],
        'sample8': [
            9,
            10
        ],
        'od': od,
        'dd': dd,
        'DecimalInt': decimal.Decimal(42),
        'DecimalFloat': decimal.Decimal(2.0)/decimal.Decimal(3.0),
        'a_tuple': (1, 2, 3),
        42: 'my_key_is_an_int',
        'difficult_floats': [math.pi, math.e, sys.float_info.max, sys.float_info.min, 0.6],
        'difficult_ints': [sys.maxsize]
    }

    pprint(sample_input)
    dynamodb_dict = dict_to_dynamodb(sample_input)
    pprint(dynamodb_dict)
    assert(dynamodb_dict['sample1'] == 'Test Data')
    assert(dynamodb_dict['sample2'] == decimal.Decimal('2'))
    assert(dynamodb_dict['sample3'] is True)
    assert(dynamodb_dict['sample5'] is None)
    assert(dynamodb_dict['sample6'] == {'test': True})
    assert(dynamodb_dict['sample7'] == ["Hello", "World"])
    assert(dynamodb_dict['sample8'] == [decimal.Decimal(9), decimal.Decimal(10)])
    assert(dynamodb_dict['DecimalInt'] == decimal.Decimal(42))
    assert(dynamodb_dict['DecimalFloat'] == decimal.Decimal(2.0)/decimal.Decimal(3.0))
    assert(dynamodb_dict['a_tuple'] == [1, 2, 3])
    assert(dynamodb_dict['42'] == 'my_key_is_an_int')  # test conversion of an int key to a string


if __name__ == "__main__":
    test_dict_to_dynamodb()
