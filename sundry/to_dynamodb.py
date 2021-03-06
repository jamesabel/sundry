import io
import decimal
from collections import OrderedDict, defaultdict
import datetime

from PIL import Image

# Handles Inexact error.
decimal_context = decimal.getcontext().copy()
decimal_context.prec = 38  # Numbers can have 38 digits precision
handle_inexact_error = True


def dict_to_dynamodb(input_value, convert_images: bool = True, raise_exception: bool = True):
    """
    makes a dictionary follow boto3 item standards

    :param input_value: input dictionary
    :param convert_images: set to False to skip over images (they can be too large)
    :param raise_exception: set to False to not raise exceptions on issues

    :return: converted version of the original dictionary

    """
    if type(input_value) is dict or type(input_value) is OrderedDict or type(input_value) is defaultdict:
        resp = {}
        for k, v in input_value.items():
            if type(k) is int:
                k = str(k)  # allow int as key since it is unambiguous (e.g. bool and float are ambiguous)
            resp[k] = dict_to_dynamodb(v, convert_images, raise_exception)
    elif type(input_value) is list or type(input_value) is tuple:
        # converts tuple to list
        resp = [dict_to_dynamodb(v, convert_images, raise_exception) for v in input_value]
    elif type(input_value) is str:
        if len(input_value) > 0:
            resp = input_value
        else:
            # DynamoDB does not allow zero length strings
            resp = None
    elif type(input_value) is bool or input_value is None or type(input_value) is decimal.Decimal:
        resp = input_value  # native DynamoDB types
    elif type(input_value) is float or type(input_value) is int:
        # boto3 uses Decimal for numbers
        # Handle the 'inexact error' via decimal_context.create_decimal
        # 'casting' to str may work as well, but decimal_context.create_decimal should be better at maintaining precision
        if handle_inexact_error:
            resp = decimal_context.create_decimal(input_value)
        else:
            resp = decimal.Decimal(input_value)
    elif isinstance(input_value, Image.Image):
        if convert_images:
            # save pillow (PIL) image as PNG binary
            image_byte_array = io.BytesIO()
            input_value.save(image_byte_array, format="PNG")
            resp = image_byte_array.getvalue()
        else:
            resp = None
    elif isinstance(input_value, datetime.datetime):
        resp = input_value.isoformat()
    else:
        if raise_exception:
            raise NotImplementedError(type(input_value), input_value)
        else:
            resp = None
    return resp
