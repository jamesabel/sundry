import decimal

# Handles Inexact error.
decimal_context = decimal.getcontext().copy()
decimal_context.prec = 38  # Numbers can have 38 digits precision


def dict_to_dynamodb(orig_dict):
    """
    makes a dictionary follow boto3 item standards
    :param orig_dict: original dictionary
    :return: converted version of the original dictionary
    """
    if type(orig_dict) is dict:
        resp = {}

        for key, value in orig_dict.items():

            if type(value) is str:
                resp[key] = value

            elif type(value) is float:
                resp[key] = decimal_context.create_decimal(value)

            elif type(value) is int:
                resp[key] = decimal_context.create_decimal(value)

            elif type(value) is dict:
                resp[key] = dict_to_dynamodb(value)

            elif type(value) is list:
                resp[key] = []
                for v in value:
                    resp[key].append(dict_to_dynamodb(v))

            elif value is None:
                pass

            else:
                resp[key] = value

    elif type(orig_dict) is not list:
        resp = None
        if type(orig_dict) is str:
            resp = orig_dict

        elif type(orig_dict) is float:
            resp = decimal.Decimal(str(orig_dict))

        elif type(orig_dict) is int:
            resp = decimal.Decimal(str(orig_dict))

        elif orig_dict is None:
            pass

        else:
            resp = orig_dict

    else:
        raise NotImplementedError

    return resp
