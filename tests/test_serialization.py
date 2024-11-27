import threading
import time

from django.core.cache import cache, caches
from django.test import override_settings, SimpleTestCase

from django_project_base.caching import CacheCounter
from django_project_base.serialization import CacheLock, NoTimeoutCheck, ObjectLockTimeout


class TestSerialization(SimpleTestCase):

    @override_settings(CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': '',
        }
    })
    def test_serialization_blocking(self):
        times = dict()
        caches["default"].clear()

        def _run_process(name):
            from django.db import connection
            nonlocal times
            times.setdefault(name, dict())
            with CacheLock("Process"):
                times[name]["start"] = time.time()
                CacheCounter("processed").incr()
                time.sleep(1)
                times[name]["end"] = time.time()
            connection.close()

        # Spawning 3 processes that tries to execute CacheLock code at the same time.
        # They should wait for each other (but order is not guaranteed).
        # I am checking if execution times of threads are not overlapping
        processes = []
        for i in range(3):
            processes.append(threading.Thread(target=_run_process, args=(f"Thread-{i + 1}",)))
        for p in processes:
            p.start()
            time.sleep(.1)
        for p in processes:
            p.join()

        self.assertEqual(cache.get("processed"), 3)
        end = 0
        for key in sorted(times.keys(), key=lambda k: times[k]["start"]):
            start = times[key]["start"]
            self.assertLessEqual(end, start)
            end = times[key]["end"]

    @override_settings(CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': '',
        }
    })
    def test_serialization_blocking_timeout(self):

        caches["default"].clear()
        expect_processed = 0
        expect_cl_timeout = 0
        expect_to_check = 0
        expect_invalid_to = 0

        def _check_counters():
            self.assertEqual(cache.get("processed", 0), expect_processed)
            self.assertEqual(cache.get("cl_timeout", 0), expect_cl_timeout)
            self.assertEqual(cache.get("to_check", 0), expect_to_check)
            self.assertEqual(cache.get("invalid_to", 0), expect_invalid_to)

        def _run_process(timeout_check, sleep, timeout):
            from django.db import connection
            try:
                with CacheLock("Process", timeout=timeout,
                               silence_object_lock_timeout=True if timeout == -1 else False) as cl:
                    if timeout_check:
                        cl()
                    CacheCounter("processed").incr()
                    if sleep:
                        time.sleep(2)
            except ObjectLockTimeout:
                CacheCounter("cl_timeout").incr()
            except NoTimeoutCheck:
                CacheCounter("to_check").incr()
            except Exception:
                CacheCounter("invalid_to").incr()
            connection.close()

        # Invalid timeout. CacheLock should raise Exception
        p = threading.Thread(target=_run_process, args=(False, False, -2))
        p.start()
        p.join()
        expect_invalid_to += 1
        _check_counters()

        # No timeout check. CacheLock should raise NoTimeoutCheck exception.
        # But this only happens on exit. So with block is processed
        p = threading.Thread(target=_run_process, args=(False, False, 1))
        p.start()
        p.join()

        expect_processed += 1
        expect_to_check += 1
        _check_counters()

        # Timeout greater than function execution time. Only first CacheLock call should be processed.
        # There should be two ObjectLockTimeout exceptions raised
        processes = []
        for i in range(3):
            processes.append(threading.Thread(target=_run_process, args=(True, True, 1)))
        for p in processes:
            p.start()
            time.sleep(.1)
        for p in processes:
            p.join()

        expect_processed += 1
        expect_cl_timeout += 2
        _check_counters()

        # Just checking if there is no lock anymore. So this call should be processed without any issues
        p = threading.Thread(target=_run_process, args=(True, False, 1))
        p.start()
        p.join()

        expect_processed += 1
        _check_counters()

        # Timeout set to -1, which means that if with block is currently executing other thread should just skip it.
        # So in this case with block should be processed only once.
        processes = []
        for i in range(3):
            processes.append(threading.Thread(target=_run_process, args=(True, True, -1)))
        for p in processes:
            p.start()
            time.sleep(.1)
        for p in processes:
            p.join()

        expect_processed += 1
        _check_counters()
