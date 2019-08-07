
import inspect


def is_main():
    """

    Prettier version of __name__ == "__main__"

    :return: True if application is running as 'main'

    """
    return inspect.stack()[1].frame.f_locals.get("__name__") == "__main__"
