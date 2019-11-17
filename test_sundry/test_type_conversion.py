from decimal import Decimal

from sundry import to_bool


def test_type_conversion():
    test_values = {
        False: [False, "F", "false", "False", "FALSE", "F", "N", "no", 0, Decimal(0), Decimal(0.0), "off"],
        True: [True, "T", "true", "yes", "Y", 1, Decimal(1), Decimal(1.0), "on"],
        None: [None, "None", "NULL", "null"],
    }
    for value, variants in test_values.items():
        for variant in variants:
            assert value == to_bool(variant)

    test_unsupported_values = {False: ["Nope", -1, "Nada", "fuggedaboutit", Decimal(-1)], True: ["Yup", "Si", 1.1, Decimal(100.0), Decimal(0.5)]}
    for value, variants in test_unsupported_values.items():
        for variant in variants:
            try:
                # should get a ValueError
                to_bool(variant)
                print(value, variant)
                assert False  # in case we don't get the ValueError
            except ValueError:
                pass  # OK


def tst_value_error():
    to_bool(-1)


if __name__ == "__main__":
    test_type_conversion()
    try:
        tst_value_error()
        assert False  # in case we don't get the ValueError
    except ValueError:
        pass
