import threading
import time

from django.core.cache import cache, caches
from django.test import override_settings, SimpleTestCase

from django_project_base.caching import CacheCounter
from django_project_base.caching.cache_queue import CacheQueue


def get_redis_cache_backend_name():
    if CacheQueue.is_redis_cache_backend("default"):
        return "django_redis.cache.RedisCache"
    else:
        return "django.core.cache.backends.locmem.LocMemCache"


class TestCaching(SimpleTestCase):
    @override_settings(
        CACHES={
            "default": {
                "BACKEND": get_redis_cache_backend_name(),
                "LOCATION": "redis://127.0.0.1:6379?db=1",
                "OPTIONS": {
                    "CLIENT_CLASS": "django_redis.client.DefaultClient",
                },
            },
        }
    )
    def test_cache_counter_redis_cache(self):
        # Calling cache counter test for redis cache backend
        self._test_cache_counter()

    @override_settings(
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
                "LOCATION": "",
            }
        }
    )
    def test_cache_counter_loc_mem_cache(self):
        # Calling cache counter test for locmem cache backend
        self._test_cache_counter()

    def _test_cache_counter(self):
        caches["default"].clear()

        # Increasing counters
        self._change_counters(True)

        for c in range(3):
            self.assertEqual(280, cache.get(f"cnt_{c + 1}", 0))

        # Decreasing counters
        self._change_counters(False)

        for c in range(3):
            self.assertEqual(0, cache.get(f"cnt_{c + 1}", 0))

        caches["default"].clear()
        # Increasing counters with start at 10
        self._change_counters(True, 10)
        for c in range(3):
            self.assertEqual(290, cache.get(f"cnt_{c + 1}", 0))

        # Checking if counter only lasts till timeout
        cc = CacheCounter("timeout", timeout=2)
        start = time.time()
        cc.incr()
        while cache.get("timeout", 0) and time.time() - start < 4:
            time.sleep(0.1)
        duration = time.time() - start
        self.assertTrue(2 < duration < 3)

        increased = False
        start = time.time()
        cc.incr()
        # Checking if counter only lasts till timeout after last change
        while cache.get("timeout", 0) and time.time() - start < 5:
            if not increased and time.time() - start > 1:
                cc.incr()
                increased = True
            time.sleep(0.1)
        duration = time.time() - start
        self.assertTrue(3 < duration < 4)

    # noinspection PyMethodMayBeStatic
    def _change_counters(self, increase=True, start=0):
        def _increase_counter(key, value):
            from django.db import connection

            counter = CacheCounter(key)
            for _i in range(10):
                params = dict()
                if value != 1:
                    params["step"] = value
                if start != 0:
                    params["start"] = start
                counter.incr(**params)
                time.sleep(0.001)
            connection.close()

        # I maintain 3 counters. Each is getting updated by 7 threads (at same time).
        # Each thread is changing counters with different step
        # So checking if all updates are taken into account.

        test_processes = []
        for i in range(7):
            for c in range(3):
                test_processes.append(
                    threading.Thread(target=_increase_counter, args=(f"cnt_{c + 1}", (i + 1) * (1 if increase else -1)))
                )
        for process in test_processes:
            process.start()

        for process in test_processes:
            process.join()

    @override_settings(
        CACHES={
            "default": {
                "BACKEND": get_redis_cache_backend_name(),
                "LOCATION": f"redis://127.0.0.1:6379?db=1",
                "OPTIONS": {
                    "CLIENT_CLASS": "django_redis.client.DefaultClient",
                },
            },
        }
    )
    def test_cache_queue_redis_cache(self):
        # Calling cache queue test for redis cache backend
        self._test_cache_queue()

    @override_settings(
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
                "LOCATION": "",
            }
        }
    )
    def test_cache_queue_loc_mem_cache(self):
        # Calling cache queue test for locmem cache backend
        self._test_cache_queue()

    def _test_cache_queue(self):
        caches["default"].clear()
        cache_queue = CacheQueue.get_cache_queue("test", timeout=None)

        # inserting data to end of queue
        cache_queue.rpush("1")
        cache_queue.rpush("2", "3", "4")
        values = ["5", "6", "7"]
        cache_queue.rpush(*values)
        whole_list = cache_queue.lrange()
        self.assertTrue(isinstance(whole_list, list))
        self.assertEqual(len(whole_list), 7)
        for i in range(7):
            self.assertEqual(whole_list[i].decode("utf-8"), str(i + 1))

        # poping data from start of queue
        first_item = cache_queue.lpop()
        # If only one item is retrieved it should not be in list
        self.assertFalse(isinstance(first_item, list))
        self.assertEqual(first_item.decode("utf-8"), "1")
        next_items = cache_queue.lpop(3)
        # If more than item is retrieved it should be in list
        self.assertTrue(isinstance(next_items, list))
        self.assertEqual(len(next_items), 3)
        for i in range(3):
            self.assertEqual(next_items[i].decode("utf-8"), str(i + 2))

        next_items = cache_queue.lpop(30)
        self.assertTrue(isinstance(next_items, list))
        self.assertEqual(len(next_items), 3)
        for i in range(3):
            self.assertEqual(next_items[i].decode("utf-8"), str(i + 5))

        next_items = cache_queue.lpop(30)
        # If there is no items in queue, pop should return None
        self.assertIsNone(next_items)

        whole_list = cache_queue.lrange()
        self.assertTrue(isinstance(whole_list, list))
        self.assertEqual(len(whole_list), 0)

        cache_queue = CacheQueue.get_cache_queue("test1")
        # inserting data to start of queue
        cache_queue.lpush("1")
        cache_queue.lpush("2", "3", "4")
        values = ["5", "6", "7"]
        cache_queue.lpush(*values)
        whole_list = cache_queue.lrange()
        self.assertTrue(isinstance(whole_list, list))
        self.assertEqual(len(whole_list), 7)
        for i in range(7):
            self.assertEqual(whole_list[i].decode("utf-8"), str(7 - i))

        # poping data from end of queue
        last_item = cache_queue.rpop()
        # If only one item is retrieved it should not be in list
        self.assertFalse(isinstance(last_item, list))
        self.assertEqual(last_item.decode("utf-8"), "1")
        prev_items = cache_queue.rpop(3)
        # If more than item is retrieved it should be in list
        self.assertTrue(isinstance(prev_items, list))
        self.assertEqual(len(prev_items), 3)
        for i in range(3):
            self.assertEqual(prev_items[i].decode("utf-8"), str(i + 2))

        prev_items = cache_queue.rpop(30)
        self.assertTrue(isinstance(prev_items, list))
        self.assertEqual(len(prev_items), 3)
        for i in range(3):
            self.assertEqual(prev_items[i].decode("utf-8"), str(i + 5))

        prev_items = cache_queue.rpop(30)
        # If there is no items in queue, pop should return None
        self.assertIsNone(prev_items)

        whole_list = cache_queue.lrange()
        self.assertTrue(isinstance(whole_list, list))
        self.assertEqual(len(whole_list), 0)

        cache_queue.set_timeout(2)
        cache_queue.rpush(b"1", b"2", b"3", b"4")
        # retrieving, but not removing items from start of queue
        next_items = cache_queue.lrange(2)
        self.assertTrue(isinstance(next_items, list))
        self.assertEqual(len(next_items), 3)
        for i in range(3):
            self.assertEqual(next_items[i], str(i + 1).encode("utf-8"))
        # removing items from start of queue
        cache_queue.ltrim(len(next_items))

        start = time.time()
        self.assertEqual(len(cache_queue.lrange()), 1)
        # Checking if queue only persists until timeout
        while cache_queue.lrange() and time.time() - start < 4:
            time.sleep(0.1)
        duration = time.time() - start
        self.assertTrue(2 < duration < 3)
