import json

from enum import Enum
from decimal import Decimal


def convert_serializable_special_cases(o):
    """
    Convert an object to a type that is fairly generally serializable (e.g. json serializable).
    This only handles the cases that need converting.  The json module handles all the rest.
    For JSON, with json.dump or json.dumps with argument default=convert_serializable.
    Example:
        json.dumps(my_animal, indent=4, default=_convert_serializable)
    :param o: object to be converted to a type that is serializable
    :return: a serializable representation
    """
    if isinstance(o, Enum):
        serializable_representation = o.value
    elif isinstance(o, Decimal):
        # decimal.Decimal (e.g. in AWS DynamoDB), both integer and floating point
        if o % 1 == 0:
            # if representable with an integer, use an integer
            serializable_representation = int(o)
        else:
            # not representable with an integer so use a float
            serializable_representation = float(o)
    else:
        raise NotImplementedError(f'can not serialize {o} since type={type(o)}')
    return serializable_representation


def make_serializable(o):
    # Convert an object to a type that is fairly generally serializable (e.g. json serializable).
    return json.loads(json.dumps(o, default=convert_serializable_special_cases, sort_keys=True))
