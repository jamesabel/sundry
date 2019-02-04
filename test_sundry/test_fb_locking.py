
import sys
import time
import logging
from sundry import FileBasedLocking
from threading import Event
from random import uniform
from multiprocessing import Process, Event

log = logging.getLogger()


class TestProcess(Process):

    class MyFileBasedLocking(FileBasedLocking):

        def get_lock_file_dir(self):
            return "temp"

        def init_logger(self):
            logging.basicConfig(stream=sys.stdout, level=logging.WARNING)

    def __init__(self, verbose=False):
        super().__init__()
        self._exit_event = Event()
        self._start_time = time.time()
        self.verbose = verbose

    def random_wait(self):
        # every so often delay a small amount of time before the next round
        wait_time = uniform(0.0, 1.0)
        self._exit_event.wait(wait_time)

    def print_stats(self, test_count, prefix=''):
        print(f"{time.time()-self._start_time}:{self.name}:{self.pid}={test_count}")

    def print(self, s):
        if self.verbose:
            print(s)

    def run(self):
        fbl = self.MyFileBasedLocking('test', timeout=5)
        test_count = 0
        while not self._exit_event.is_set():
            self.print(f"{self.name} waiting")
            lock_uuid = fbl.acquire_lock()
            assert (lock_uuid is not None)
            self.print(f"{self.name} working")
            self.random_wait()  # the 'work' while locked
            fbl.relinquish_lock(lock_uuid)
            self.print(f"{self.name} stopped")
            self.random_wait()  # the other 'work'
            test_count += 1
        self.print_stats(test_count)

    def request_exit(self):
        self._exit_event.set()


def test_fb_locking(run_time=4*60*60):

    n_processes = 30
    processes = []

    for process_number in range(0, n_processes):
        processes.append(TestProcess())
    for p in processes:
        p.start()

    time.sleep(run_time)

    print('**** stopping all ****')
    for p in processes:
        p.request_exit()
    for p in processes:
        p.join()


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.WARNING)
    test_fb_locking()
