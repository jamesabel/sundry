import os
import inspect


def get_func_name() -> str:
    """
    get name of the *calling* function
    :return: name of the calling function
    """
    return inspect.stack()[1].frame.f_code.co_name


def get_line_number() -> str:
    """
    get line number of the *calling* function
    :return: line number of the calling function
    """
    return inspect.stack()[1].frame.f_lineno


def get_file_name() -> str:
    """
    get base file name (i.e. just the file name - not the entire path) of the *calling* function
    :return: file name of the calling function
    """
    return os.path.basename(inspect.stack()[1].frame.f_code.co_filename)


def get_file_path() -> str:
    """
    get file path of the *calling* function
    :return: file path of the calling function
    """
    return inspect.stack()[1].frame.f_code.co_filename
