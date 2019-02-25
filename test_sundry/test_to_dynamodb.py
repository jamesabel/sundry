
import decimal
from pprint import pprint

from sundry import dict_to_dynamodb


def test_dict_to_dynamodb():

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
        ]
    }

    dynamodb_dict = dict_to_dynamodb(sample_input)
    pprint(dynamodb_dict)
    assert(dynamodb_dict['sample1'] == 'Test Data')
    assert(dynamodb_dict['sample2'] == decimal.Decimal('2'))
    assert(dynamodb_dict['sample3'] is True)
    assert('sample5' not in dynamodb_dict.keys())
    assert(dynamodb_dict['sample6'] == {'test': True})
    assert(dynamodb_dict['sample7'] == ["Hello", "World"])
    assert(dynamodb_dict['sample8'] == [decimal.Decimal(9), decimal.Decimal(10)])


if __name__ == "__main__":
    test_dict_to_dynamodb()
