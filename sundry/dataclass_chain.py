from dataclasses import dataclass, fields


def dataclass_chain(klass: dataclass, *dataclass_instances: dataclass, raise_exception: bool = True):
    """
    Combine multiple dataclass objects into one.

    :param klass: dataclass class (not instance)
    :param dataclass_instances: one or more dataclass instances
    :param raise_exception: True to raise chain value mismatch exception, False to merely have earlier instances override earlier ones (similar to ChainMap)
    :return: a dataclass instance whose contents is the combination of the args dataclass instances
    """
    chain = klass()

    for dataclass_instance in dataclass_instances:
        for field in fields(klass):
            field_name = field.name
            if hasattr(dataclass_instance, field_name):
                value = getattr(dataclass_instance, field_name)
                if value is not None:
                    existing_value = getattr(chain, field_name)
                    if existing_value is None:
                        setattr(chain, field_name, value)
                    elif value != existing_value and raise_exception:
                        raise ValueError("conflict", f"{field_name=}", chain, dataclass_instance)

    return chain
