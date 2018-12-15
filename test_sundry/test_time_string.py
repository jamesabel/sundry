import time

from sundry import local_time_string, utc_time_string


def test_time_string():
    t = time.time()
    lts = local_time_string(t)
    uts = utc_time_string(t)
    for ts in [lts, uts]:
        # basic check for a few fields
        assert(ts[0:1] == '2')
        assert(ts.find('-') == 4)
        assert(ts.find(':') == 13)
        print(ts)
