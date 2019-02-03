
import os
import logging
from uuid import uuid4
from os import makedirs
import time

log = logging.getLogger(__name__)


class FileBasedLocking:
    """
    Lock some thing, using a file in the local file system.
    """
    def __init__(self, application_name=None, author_name=None, timeout=30):
        self.application_name = application_name
        self.author_name = author_name
        self.timeout = timeout

    def get_lock_file_dir(self):
        """
        Return the directory the lock file will be in.  Override this method to change the directory used.
        For example, use appdirs' user_data_dir() instead of site_data_dir() for user scope (instead of system scope).

        from appdirs import site_data_dir
        return os.path.join(site_data_dir(self.application_name, self.author_name))

        :return: lock file directory
        """
        return "."

    def get_lock_file_name(self, application_name):
        return f'{application_name}_fbl.txt'  # file based lock

    def get_lock_file_path(self):
        return os.path.join(self.get_lock_file_dir(), self.get_lock_file_name(self.application_name))

    def _get_time(self):
        """
        Gets the time as a string in a very specific format and number of characters.
        :return: time since epoch as a constant-length string
        """
        return f"{time.time():30.6f}"

    def _write_lock_string(self, f, lock_uuid):
        f.write(f"L,{lock_uuid},{self._get_time()}")

    def acquire_lock(self):
        """
        Acquire the lock.  Returns the UUID of this lock if successful, otherwise None.
        :return: Lock UUID or None if failure.
        """
        lock_acquired = False
        lock_uuid = str(uuid4())
        lock_file_path = self.get_lock_file_path()
        makedirs(os.path.dirname(lock_file_path), exist_ok=True)
        timeout_count = self.timeout
        while not lock_acquired and timeout_count > 0:
            write_lock = False
            try:
                with open(lock_file_path, 'r+') as f:
                    contents = f.read()
                    contents_list = contents.split(',')
                    file_age = time.time() - float(contents_list[2])
                    if contents[0] == '_':
                        write_lock = True
                        log.info(f"locking unlocked file {lock_file_path}")
                    elif file_age > self.timeout:
                        write_lock = True
                        log.warning(f'locking timed out file="{lock_file_path}",file_age={file_age},timeout={self.timeout},contents="{contents}"')
                    else:
                        log.info(f"waiting for {lock_file_path}, locked by {contents_list[1]} , lock age={file_age}")
                    if write_lock:
                        f.seek(0)
                        self._write_lock_string(f, lock_uuid)
            except FileNotFoundError:
                with open(lock_file_path, 'w') as f:
                    self._write_lock_string(f, lock_uuid)

            # check that we actually got the lock
            try:
                with open(lock_file_path) as f:
                    file_lock_id = f.read().split(',')[1]
                    if file_lock_id == lock_uuid:
                        lock_acquired = True
                    else:
                        log.info(f"{file_lock_id} != {lock_uuid}")
            except FileNotFoundError as e:
                log.warning(f"{lock_file_path} {e}")
            except IOError as e:
                log.warning(f"{lock_file_path} {e}")

            if not lock_acquired:
                time.sleep(1)
            timeout_count -= 0

        if not lock_acquired:
            log.error(f"lock not acquired")
        return lock_uuid if lock_acquired else None

    def relinquish_lock(self, lock_uuid):
        assert(lock_uuid is not None)
        lock_relinquished = False
        lock_file_path = self.get_lock_file_path()
        timeout_count = self.timeout
        while not lock_relinquished and timeout_count > 0:
            try:
                with open(lock_file_path, 'r+') as f:
                    file_lock_uuid = f.read().split(',')[1]
                    if file_lock_uuid == lock_uuid:
                        f.seek(0)
                        f.write('_')  # signal unlocked with an underscore in character position 0
                        lock_relinquished = True
                        log.info(f"relinquished {lock_uuid}")
                    else:
                        log.warning(f"looking for {lock_uuid} but got {file_lock_uuid}")
            except FileNotFoundError as e:
                log.warning(f"{lock_file_path} {e}")
            except IOError as e:
                log.warning(f"{lock_file_path} {e}")
            timeout_count -= 1
            if not lock_relinquished:
                time.sleep(1)
        return lock_relinquished
