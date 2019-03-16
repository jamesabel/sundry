
import decimal
from collections import OrderedDict, defaultdict

# Handles Inexact error.
decimal_context = decimal.getcontext().copy()
decimal_context.prec = 38  # Numbers can have 38 digits precision
handle_inexact_error = True


def dict_to_dynamodb(input_value):
    """
    makes a dictionary follow boto3 item standards
    :param input_value: input dictionary
    :return: converted version of the original dictionary
    """
    if type(input_value) is dict or type(input_value) is OrderedDict or type(input_value) is defaultdict:
        resp = {}
        for k, v in input_value.items():
            if type(k) is int:
                k = str(k)  # allow int as key since it is unambiguous (e.g. bool and float are ambiguous)
            resp[k] = dict_to_dynamodb(v)
    elif type(input_value) is list or type(input_value) is tuple:
        # converts tuple to list
        resp = [dict_to_dynamodb(v) for v in input_value]
    elif type(input_value) is str or type(input_value) is bool or input_value is None or type(input_value) is decimal.Decimal:
        resp = input_value  # native DynamoDB types
    elif type(input_value) is float or type(input_value) is int:
        # boto3 uses Decimal for numbers
        # Handle the 'inexact error' via decimal_context.create_decimal
        # 'casting' to str may work as well, but decimal_context.create_decimal should be better at maintaining precision
        if handle_inexact_error:
            resp = decimal_context.create_decimal(input_value)
        else:
            resp = decimal.Decimal(input_value)
    else:
        raise NotImplementedError(type(input_value), input_value)
    return resp
