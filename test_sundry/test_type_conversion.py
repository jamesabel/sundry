
from sundry import to_bool


def test_type_conversion():
    test_values = {False: ['F', 'false', 'False', 'FALSE', 'no', 0],
                   True: ['T', 'true', 'yes', 1],
                   None: [None, 'None', 'NULL', 'null']}
    for value, variants in test_values.items():
        for variant in variants:
            assert value == to_bool(variant)

    test_unsupported_values = {False: ['Nope', -1, 'Nada', 'fuggedaboutit'],
                               True: ['Yup', 'Si', 1.1]}
    for value, variants in test_unsupported_values.items():
        for variant in variants:
            try:
                # should get a ValueError
                to_bool(variant)
                assert False  # in case we don't get the ValueError
            except ValueError:
                pass  # OK


def tst_value_error():
    to_bool(-1)


if __name__ == '__main__':
    tst_value_error()
