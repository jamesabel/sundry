
import sys
import time
import logging
import os
import random
from sundry import FileBasedLocking
import multiprocessing.managers

from balsa import Balsa, get_logger
from pressenter2exit import PressEnter2Exit

application_name = 'test_fb_locking'
author_name = 'abel'

log = get_logger(application_name)

temp_dir = 'temp'


def get_out_file_path():
    return os.path.join('temp', 'fb_locking_test_out.txt')


def append_out_file(s):
    out_file_path = get_out_file_path()
    if os.path.exists(out_file_path):
        mode = 'a'
    else:
        mode = 'w'
    os.makedirs(os.path.dirname(out_file_path), exist_ok=True)
    with open(get_out_file_path(), mode) as f:
        f.write(s)


def get_inc_file_path():
    return os.path.join(temp_dir, 'inc_file.txt')


def read_work_file(caller_uuid, caller_process_name, caller_count):
    file_value = None
    with open(get_inc_file_path()) as f:
        s = f.read()
        if s is not None and len(s) > 0:
            file_value_string, file_uuid, file_process_name = s.split(',')
            try:
                file_value = int(file_value_string)
            except ValueError as e:
                print(f"{caller_uuid} {e}")
        else:
            file_value_string = None
            file_uuid = None
            file_process_name = None
    if file_value is None:
        sys.exit(caller_uuid)

    s = f"{file_value},r,{file_uuid},{file_process_name},{caller_uuid},{caller_process_name},{caller_count}"
    append_out_file(f"{s}\n")
    # print(s)

    return file_value, file_value_string


def write_work_file(file_value, test_uuid, process_name, stats):

    s = f"{file_value},w,{test_uuid},{process_name},{stats}"
    append_out_file(f"{s}\n")
    # print(s)

    inc_file_path = get_inc_file_path()
    os.makedirs(os.path.dirname(inc_file_path), exist_ok=True)
    with open(inc_file_path, 'w') as f:
        int(f.write(f"{file_value},{test_uuid},{process_name}"))


class TstProcess(multiprocessing.Process):

    class MyFileBasedLocking(FileBasedLocking):

        def get_lock_file_dir(self):
            return temp_dir

        def init_logger(self):
            balsa_log = Balsa(self.instance_name, author_name, log_directory=os.path.join('temp', 'log'), delete_existing_log_files=True)
            balsa_log.init_logger()
            self.log = get_logger(application_name)

    def __init__(self, iterations, verbose):
        super().__init__()
        self._start_time = time.time()
        self.iterations = iterations
        self.verbose = verbose

    def print_stats(self, test_count, stats):
        print(f"*** done:{time.time()-self._start_time}:{self.name}:{self.pid}:iterations={test_count}:{stats} ***")

    def print(self, s):
        if self.verbose:
            print(s)

    def _stats_to_dict(self, total_time, test_count, min_time, max_time):
        return {'avg': total_time/float(test_count), 'min': min_time, 'max': max_time}

    def run(self):
        fbl = self.MyFileBasedLocking('test', instance_name=self.name)
        fbl.log_name = self.name
        test_count = 0
        total_time = 0.0
        min_time = None
        max_time = None

        while test_count < self.iterations:
            self.print(f"{self.name} waiting")

            start_time = time.time()
            lock_uuid = fbl.acquire_lock()
            duration = time.time() - start_time
            total_time += duration
            min_time = duration if min_time is None else min(min_time, duration)
            max_time = duration if max_time is None else max(max_time, duration)

            assert (lock_uuid is not None)
            self.print(f"{self.name} working ({lock_uuid})")
            file_test_count, file_uuid = read_work_file(lock_uuid, self.name, test_count)
            time.sleep(random.uniform(0.0, 1.0))  # work while this process owns the lock
            test_count += 1
            write_work_file(file_test_count + 1, lock_uuid, self.name, self._stats_to_dict(total_time, test_count, min_time, max_time))
            fbl.relinquish_lock(lock_uuid)
            time.sleep(random.uniform(0.0, 1.0))  # 'other work' (while this process does NOT own the lock)
            self.print(f"{self.name} stopped")
        self.print_stats(test_count, self._stats_to_dict(total_time, test_count, min_time, max_time))


def test_fb_locking(long_test=False):

    if long_test:
        overall_time = 4*60*60  # approximate run time in seconds
        n_processes = 13
        iterations = int(round(float(overall_time)/float(n_processes))/2.0)  # div by 2 to get approximately the overall runtime
        print(f"{iterations} iterations")
    else:
        # short test (e.g. pytest)
        n_processes = 3
        iterations = 5

    processes = []
    try:
        os.remove(get_out_file_path())
    except FileNotFoundError:
        pass

    try:
        os.remove(os.path.join(temp_dir, 'test_fbl.txt'))
    except FileNotFoundError:
        pass
    write_work_file(0, 'INIT', 'INIT', 'INIT')
    for process_number in range(0, n_processes):
        processes.append(TstProcess(iterations, False))
    for p in processes:
        p.start()

    time.sleep(2)  # processes will not run without this (!)

    if long_test:
        press_enter_to_exit = PressEnter2Exit(pre_message=f'press enter to force exit of {application_name}',
                                              post_message=f'"{application_name}" has been forced to exit ...')
    else:
        press_enter_to_exit = None  # don't use stdout when running pytest
    print()
    while (press_enter_to_exit is None or press_enter_to_exit.is_alive()) and all([p.is_alive() for p in processes]):
        time.sleep(1)
    if press_enter_to_exit is not None and not press_enter_to_exit.is_alive():
        for p in processes:
            p.kill()
    for p in processes:
        p.join()
    total_iterations, _ = read_work_file('FINAL', 'FINAL', 'FINAL')
    print(f"iterations : got {total_iterations}, expected {n_processes * iterations}")
    assert(total_iterations == n_processes * iterations)


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.WARNING)
    test_fb_locking(True)  # long test
