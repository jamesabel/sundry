
import os
import sys
import logging
from uuid import uuid4
from os import makedirs
import time

fb_locking_name = 'fb_locking'

lock_char = 'L'
unlock_char = '_'
separator_char = ','

log = logging.getLogger()


class FileBasedLocking:

    """

    Lock some thing, using a file in the local file system as the lock mechanism.

    """

    def __init__(self, application_name=None, author_name=None, timeout=10*60, instance_name=''):

        log.warning("FileBasedLocking has been deprecated and will be removed")

        self.application_name = application_name
        self.author_name = author_name
        self.timeout = timeout  # seconds
        self.instance_name = instance_name

        self.lock_acquired_threshold = 5  # lock file needs to be constant for this number of consecutive reads to be deemed stable
        self.poll_time = 1.0  # lock file needs to be constant for this time (in seconds) to be deemed stable
        self.poll_sleep_time = self.poll_time / float(self.lock_acquired_threshold)

        self.last_lock_not_acquired_message = (None, None)
        self.log = logging.getLogger(fb_locking_name)
        self.init_logger()

    def init_logger(self):

        """

        Derived class should generally override this method.  While this provided method may work for some very simple applications,
        using the Balsa package (https://pypi.org/project/balsa/) is recommended.

        For example:

            balsa_log = Balsa(application_name, author_name)
            balsa_log.init_logger()

        """

        logging.basicConfig(stream=sys.stdout, level=logging.WARNING)

    def get_lock_file_dir(self):

        """

        Return the directory the lock file will be in.  Override this method to change the directory used.

        For example, use appdirs' user_data_dir() for user scope or site_data_dir() for system scope:

        from appdirs import site_data_dir

        return os.path.join(site_data_dir(self.application_name, self.author_name))
        or
        return os.path.join(user_data_dir(self.application_name, self.author_name))

        :return: lock file directory

        """

        return "."

    def get_lock_file_name(self, application_name):
        return f'{application_name}_fbl.txt'  # file based lock

    def get_lock_file_path(self):
        return os.path.join(self.get_lock_file_dir(), self.get_lock_file_name(self.application_name))

    def _get_time(self):
        """
        Gets the time as a string in a very specific format and number of characters.  A constant string length
        facilitates updating the lock file as each field occupies a specific file offset.

        :return: time since epoch as a constant-length string
        """
        return f"{time.time():30.6f}"

    def _get_instance_name(self):
        """
        get instance name truncated and padded to a constant number of characters

        :return: instance name as an exact number of characters
        """
        return f"{self.instance_name:40.40}"

    def _write_lock_string(self, file_path, lock_uuid):
        string_verified = False
        s = separator_char.join([lock_char, lock_uuid, self._get_time(), self._get_instance_name()])
        while not string_verified:
            with open(file_path, 'w') as f:
                f.write(s)
                self.log.debug(f"writing {f.name} : {s}")
            try:
                with open(file_path) as f:
                    string_verified = s == f.read()
            except PermissionError:
                pass
            if not string_verified:
                time.sleep(self.poll_sleep_time)

    def _is_lock_acquired(self, lock_acquired_count):
        return lock_acquired_count >= self.lock_acquired_threshold

    def acquire_lock(self):
        """
        Acquire the lock.  Returns the UUID of this lock if successful, otherwise None.

        :return: Lock UUID or None if failure.
        """
        lock_acquired_count = 0
        lock_uuid = str(uuid4())
        lock_file_path = self.get_lock_file_path()
        makedirs(os.path.dirname(lock_file_path), exist_ok=True)
        timeout_count = self._get_timeout_count()
        while not self._is_lock_acquired(lock_acquired_count) and timeout_count > 0:
            time.sleep(self.poll_sleep_time)
            write_lock = False
            try:
                with open(lock_file_path, 'r+') as f:
                    contents = f.read()
                    if contents is not None and len(contents) >= 1:
                        contents_list = contents.split(separator_char)
                        file_uuid = contents_list[1]
                        file_age = time.time() - float(contents_list[2])
                        if contents[0] == unlock_char:
                            write_lock = True
                            self.log.info(f"{self.instance_name}:attempting to lock unlocked file {lock_file_path} file_uuid={file_uuid} --> {lock_uuid}")
                        elif file_age > self.timeout:
                            write_lock = True
                            self.log.warning(f'{self.instance_name}:locking timed out file="{lock_file_path}",file_age={file_age},timeout={self.timeout},lock_uuid={lock_uuid},contents="{contents}"')
                        else:
                            self.log.debug(f"{self.instance_name}:waiting for {lock_file_path}, locked by {file_uuid} , lock age={file_age}")
                    else:
                        self.log.info(f'{self.instance_name}:could not properly read "{lock_file_path}" - got "{contents}"')
            except FileNotFoundError:
                write_lock = True
            if write_lock:
                self._write_lock_string(lock_file_path, lock_uuid)

            # check that the above write actually ended up in the file (it might not)
            try:
                with open(lock_file_path) as f:
                    contents = f.read()
                    if contents is not None and len(contents) > 0:
                        contents_list = contents.split(separator_char)
                        file_lock_id = contents_list[1]
                        if contents_list[0] == lock_char and file_lock_id == lock_uuid:
                            lock_acquired_count += 1
                            self.log.info(f"{self.instance_name}:lock acquired {lock_uuid} : lock_acquired_count={lock_acquired_count}")
                        else:
                            if self.last_lock_not_acquired_message != (file_lock_id, lock_uuid):
                                self.log.info(f"{self.instance_name}:lock not acquired since {lock_uuid} != {file_lock_id} : lock_acquired_count={lock_acquired_count}")
                                self.last_lock_not_acquired_message = (file_lock_id, lock_uuid)
                            lock_acquired_count = 0
            except FileNotFoundError as e:
                self.log.warning(f"{self.instance_name}:{lock_file_path} {e}")
            except IOError as e:
                self.log.warning(f"{self.instance_name}:{lock_file_path} {e}")

            timeout_count -= 1

        if not self._is_lock_acquired(lock_acquired_count):
            self.log.error(f"{self.instance_name}:lock not acquired")
        return lock_uuid if self._is_lock_acquired(lock_acquired_count) else None

    def relinquish_lock(self, lock_uuid):
        assert(lock_uuid is not None)
        lock_relinquished = False
        lock_file_path = self.get_lock_file_path()
        timeout_countdown = self._get_timeout_count()
        while not lock_relinquished and timeout_countdown > 0:
            try:
                with open(lock_file_path, 'r+') as f:
                    contents = f.read()
                    if contents is not None and len(contents) > 0:
                        file_lock_uuid = contents.split(separator_char)[1]
                        if file_lock_uuid == lock_uuid:
                            f.seek(0)
                            f.write(unlock_char)  # signal unlocked with an underscore in character position 0
                            lock_relinquished = True
                            self.log.info(f"{self.instance_name}:relinquished {lock_uuid}")
                        else:
                            self.log.info(f"{self.instance_name}:looking for {lock_uuid} but got {file_lock_uuid}")
                    else:
                        self.log.info(f"{self.instance_name}:{lock_file_path} empty")
            except FileNotFoundError as e:
                self.log.warning(f"{self.instance_name}:{lock_file_path} {e}")
            except IOError as e:
                self.log.warning(f"{self.instance_name}:{lock_file_path} {e}")
            timeout_countdown -= 1
            if not lock_relinquished:
                time.sleep(self.poll_sleep_time)
        return lock_relinquished

    def _get_timeout_count(self):
        return round(float(self.timeout) / float(self.poll_sleep_time))
