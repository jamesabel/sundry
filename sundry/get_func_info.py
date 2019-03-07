
import inspect


def get_func_name() -> str:
    """
    get name of the *calling* function
    :return: name of the calling function
    """
    return inspect.stack()[1].frame.f_code.co_name


def get_line_number() -> str:
    """
    get name of the *calling* function
    :return: name of the calling function
    """
    return inspect.stack()[1].frame.f_lineno
