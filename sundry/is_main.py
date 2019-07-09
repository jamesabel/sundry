
import inspect


def is_main():
    return inspect.stack()[1].frame.f_locals.get("__name__") == "__main__"
