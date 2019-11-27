import os
import stat
import shutil
import time
import logging

from sundry import __title__

# more robust OS functions

log = logging.getLogger(__title__)


def remove_readonly(path: str):
    os.chmod(path, stat.S_IWRITE)


# sometimes needed for Windows
def _remove_readonly_onerror(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def rmdir(p: str):
    retry_count = 10
    delete_ok = False
    while os.path.exists(p) and retry_count > 0:
        try:
            shutil.rmtree(p, onerror=_remove_readonly_onerror)
            delete_ok = True
        except FileNotFoundError as e:
            log.debug(str(e))  # this can happen when first doing the shutil.rmtree()
            time.sleep(1)
        except PermissionError as e:
            log.info(str(e))
            time.sleep(1)
        retry_count -= 1
    if os.path.exists(p):
        log.error('could not remove "%s"' % p)
    return delete_ok and retry_count > 0


def mkdirs(d: str, remove_first=False):
    if remove_first:
        rmdir(d)
    # sometimes when os.makedirs exits the dir is not actually there
    count = 600
    while count > 0 and not os.path.exists(d):
        try:
            # for some reason we can get the FileNotFoundError exception
            os.makedirs(d, exist_ok=True)
        except FileNotFoundError:
            pass
        if not os.path.exists(d):
            time.sleep(0.1)
        count -= 1
    if not os.path.exists(d):
        log.error(f'could not mkdirs "{d}" ({os.path.abspath(d)})')
