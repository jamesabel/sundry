
import sys
import decimal
from collections import OrderedDict, defaultdict
from pprint import pprint
import math

import boto3
from botocore.exceptions import ProfileNotFound

from sundry import dict_to_dynamodb


def test_dict_to_dynamodb():

    id_str = 'id'
    dict_id = 'test'
    sundry_str = 'sundry'
    aws_region = 'us-west-2'

    od = OrderedDict()
    od['a'] = 1
    od['b'] = 2

    dd = defaultdict(int)
    dd[1] = 2

    sample_input = {
        id_str: dict_id,
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
        'difficult_floats': [math.pi, math.e, 0.6],
        'difficult_ints': [sys.maxsize]
    }

    if False:
        # interestingly, these do not work
        sample_input['does_not_work'] = [sys.float_info.max, sys.float_info.min]

    dynamodb_dict = dict_to_dynamodb(sample_input)

    assert(dynamodb_dict['sample1'] == 'Test Data')
    assert(math.isclose(float(dynamodb_dict['sample2']), decimal.Decimal(2.0)))
    assert(dynamodb_dict['sample3'] is True)
    assert(dynamodb_dict['sample5'] is None)
    assert(dynamodb_dict['sample6'] == {'test': True})
    assert(dynamodb_dict['sample7'] == ["Hello", "World"])
    assert(dynamodb_dict['sample8'] == [decimal.Decimal(9), decimal.Decimal(10)])
    assert(dynamodb_dict['DecimalInt'] == decimal.Decimal(42))
    assert(dynamodb_dict['DecimalFloat'] == decimal.Decimal(2.0)/decimal.Decimal(3.0))
    assert(dynamodb_dict['a_tuple'] == [1, 2, 3])
    assert(dynamodb_dict['42'] == 'my_key_is_an_int')  # test conversion of an int key to a string

    try:
        session = boto3.Session(profile_name=sundry_str, region_name=aws_region)
        dynamodb_resource = session.resource('dynamodb')
        table = dynamodb_resource.Table(sundry_str)
        table.put_item(Item=dynamodb_dict)
        item = table.get_item(Key={id_str: dict_id})
        sample_from_db = item['Item']
        assert(sample_from_db == dynamodb_dict)  # make sure we get back exactly what we wrote
    except ProfileNotFound as e:
        print(f'*** ERROR : could not get AWS profile "{sundry_str}" - could not test actual AWS access ***')
        print(e)
        # set to False pass even if we only test to check the conversion, although running the test doesn't actually check put/get from AWS
        if True:
            raise


if __name__ == "__main__":
    test_dict_to_dynamodb()
