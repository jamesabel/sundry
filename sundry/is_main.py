import inspect
from logging import getLogger

from sundry.__version__ import __title__

log = getLogger(__title__)


def is_main():
    """

    Prettier version of __name__ == "__main__"

    :return: True if application is running as 'main'

    """
    log.info("recommendation: use is_main() from ismain package on PyPI instead of this package (sundry)")
    return inspect.stack()[1].frame.f_locals.get("__name__") == "__main__"
