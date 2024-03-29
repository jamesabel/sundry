import os
import sys
import decimal
from collections import OrderedDict, defaultdict
from pprint import pprint
import math
import datetime
from datetime import timedelta
import pickle

from PIL import Image

import boto3
from botocore.exceptions import ProfileNotFound

from sundry import dict_to_dynamodb, aws_dynamodb_scan_table, aws_dynamodb_scan_table_cached, dict_is_close, aws_get_dynamodb_table_names

id_str = "id"
dict_id = "test"
# sundry_str = "sundry"
sundry_str = "default"
aws_region = "us-west-2"

# source:
# https://en.wikipedia.org/wiki/Portable_Network_Graphics
# https://en.wikipedia.org/wiki/File:PNG_transparency_demonstration_1.png
png_image = Image.open(os.path.join("test_sundry", "280px-PNG_transparency_demonstration_1.png"))

od = OrderedDict()
od["a"] = 1
od["b"] = 2

dd = defaultdict(int)
dd[1] = 2

sample_input = {
    id_str: dict_id,
    "sample1": "Test Data",
    "sample2": 2.0,
    "sample3": True,
    "sample4": int(1),
    "sample5": None,
    "sample6": {"test": True},
    "sample7": ["Hello", "World"],
    "sample8": [9, 10],
    "od": od,
    "dd": dd,
    "DecimalInt": decimal.Decimal(42),
    "DecimalFloat": decimal.Decimal(2.0) / decimal.Decimal(3.0),
    "a_tuple": (1, 2, 3),
    42: "my_key_is_an_int",
    "difficult_floats": [math.pi, math.e, 0.6],
    "difficult_ints": [sys.maxsize],
    "image": png_image,
    "test_date_time": datetime.datetime.fromtimestamp(1559679535),  # 2019-06-04T13:18:55
    "zero_len_string": "",
}


def check_table_contents(contents):
    with open(os.path.join("cache", f"{sundry_str}.pickle"), "rb") as f:
        assert dict_is_close(sample_input, contents[0])
        assert dict_is_close(sample_input, pickle.load(f)[0])


def test_aws():

    return

    if False:
        # interestingly, these do not work
        sample_input["does_not_work"] = [sys.float_info.max, sys.float_info.min]

    dynamodb_dict = dict_to_dynamodb(sample_input)

    assert dynamodb_dict["sample1"] == "Test Data"
    assert math.isclose(float(dynamodb_dict["sample2"]), decimal.Decimal(2.0))
    assert dynamodb_dict["sample3"] is True
    assert dynamodb_dict["sample5"] is None
    assert dynamodb_dict["sample6"] == {"test": True}
    assert dynamodb_dict["sample7"] == ["Hello", "World"]
    assert dynamodb_dict["sample8"] == [decimal.Decimal(9), decimal.Decimal(10)]
    assert dynamodb_dict["DecimalInt"] == decimal.Decimal(42)
    assert dynamodb_dict["DecimalFloat"] == decimal.Decimal(2.0) / decimal.Decimal(3.0)
    assert dynamodb_dict["a_tuple"] == [1, 2, 3]
    assert dynamodb_dict["42"] == "my_key_is_an_int"  # test conversion of an int key to a string
    assert dynamodb_dict["test_date_time"] == "2019-06-04T13:18:55"
    assert dynamodb_dict["zero_len_string"] is None

    try:
        session = boto3.Session(profile_name=sundry_str, region_name=aws_region)
        dynamodb_resource = session.resource("dynamodb")
        table = dynamodb_resource.Table(sundry_str)
        table.put_item(Item=dynamodb_dict)
        item = table.get_item(Key={id_str: dict_id})
        sample_from_db = item["Item"]
        assert sample_from_db == dynamodb_dict  # make sure we get back exactly what we wrote
    except ProfileNotFound as e:
        print(f'*** ERROR : could not get AWS profile "{sundry_str}" - could not test actual AWS access ***')
        print(e)
        # set to False pass even if we only test to check the conversion, although running the test doesn't actually check put/get from AWS
        if True:
            raise

    aws_profile = "default"  # I don't know why I need to use "default" and not "sundry"

    table_contents = aws_dynamodb_scan_table_cached(sundry_str, aws_profile, cache_life=timedelta(seconds=1).total_seconds())
    check_table_contents(table_contents)
    table_contents = aws_dynamodb_scan_table(sundry_str, aws_profile)
    check_table_contents(table_contents)
    table_contents = aws_dynamodb_scan_table_cached(sundry_str, aws_profile, cache_life=timedelta(hours=1).total_seconds())
    check_table_contents(table_contents)

    dynamodb_tables = aws_get_dynamodb_table_names(aws_profile)
    print(dynamodb_tables)
    assert(len(dynamodb_tables) > 0)
    assert('sundry' in dynamodb_tables)


if __name__ == "__main__":
    test_aws()
