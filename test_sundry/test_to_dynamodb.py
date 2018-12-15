
import decimal

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
        ]
    }

    dynamodb_dict = dict_to_dynamodb(sample_input)
    assert(dynamodb_dict['sample1'] == 'Test Data')
    assert(dynamodb_dict['sample2'] == decimal.Decimal('2'))
    assert(dynamodb_dict['sample3'] is True)
    assert('sample5' not in dynamodb_dict.keys())
    assert(dynamodb_dict['sample6'] == {'test': True})
    assert(dynamodb_dict['sample7'] == ["Hello", "World"])
