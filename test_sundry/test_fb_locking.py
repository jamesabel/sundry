
import os
from sundry import FileBasedLocking


def test_fb_locking():

    class MyFileBasedLocking(FileBasedLocking):

        def get_lock_file_dir(self):
            return "temp"

    application_name = 'myapp'

    # todo: create multiple processes all trying to access this lock simultaneously

    fbl = MyFileBasedLocking(application_name)
    lock_uuid = fbl.acquire_lock()
    assert(lock_uuid is not None)
    fbl.relinquish_lock(lock_uuid)

    os.remove(fbl.get_lock_file_path())  # start with no lock file
    lock_uuid = fbl.acquire_lock()
    assert(lock_uuid is not None)
    fbl.relinquish_lock(lock_uuid)

    fbl_b = MyFileBasedLocking(application_name, timeout=5)
    lock_uuid_b = fbl_b.acquire_lock()
    fbl_b.relinquish_lock(lock_uuid_b)


if __name__ == "__main__":
    import logging
    import sys

    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    test_fb_locking()
