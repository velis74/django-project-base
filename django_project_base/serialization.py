import time

from django.core.cache import cache

from django_project_base.caching import CacheCounter


class ObjectLockTimeout(Exception):
    """ Exception raised when a lock timeout is exceeded."""


class NoTimeoutCheck(Exception):
    """
    Exception raised when timeout is set, but not checked.
    Example:
    with CacheLock as cl:
        cl()  # this calls timeout check
        ...
        ...
    """


class CacheLock(object):
    is_waiting = False
    waiting_counter = None

    def __init__(self, name, timeout=0, silence_object_lock_timeout=False, stats_name=None):
        """
        :param name: name of the cache
        :param timeout: timeout in seconds.
            If timeout is 0, no timeout.
            If timeout is -1, code in with block will not be executed if another process is already executing it
        :param silence_object_lock_timeout: True means no exception will be raised if object lock timeout is exceeded.

        If timeout is != 0, timeout check must be called first thing in with block.
        with CacheLock(name='mycache', timeout=1) as cl:
            cl()
            ...
            ...
            rest of code in with block
            ...
            ...
        """
        if timeout is None or (timeout < 0 and timeout != -1):
            raise Exception("Invalid timeout value")

        self.name = "CacheLock." + name
        self.stats_name = "CacheLock." + (stats_name or name)
        self.timeout = timeout
        self.silence_object_lock_timeout = silence_object_lock_timeout
        self.raise_timeout_exception = False
        self.timeout_checked = False

    # noinspection PyMethodMayBeStatic
    def append_waiting_key(self, key):
        if not cache.has_key(f"Inserted.{key}"):
            cache.set(f"Inserted.{key}", True, timeout=None)
            from django_project_base.caching.cache_queue import CacheQueue

            CacheQueue.get_cache_queue("CacheLockKeys", timeout=None).rpush(key)

    def set_waiting(self, is_waiting):
        if is_waiting:
            if not self.is_waiting:
                self.is_waiting = True
                key = f"Waiting.{self.stats_name}"
                self.waiting_counter = CacheCounter(key, timeout=None)
                self.waiting_counter.incr()
                self.append_waiting_key(key)
        elif self.is_waiting and not is_waiting:
            self.waiting_counter.incr(step=-1)

    def __enter__(self):
        try:
            start_time = time.time()
            while True:
                res = CacheCounter(self.name, timeout=None).incr()
                if res == 1:
                    self.set_waiting(False)
                    break
                elif self.timeout == -1:
                    self.raise_timeout_exception = True
                    break
                self.set_waiting(True)
                time.sleep(0.1)
                if 0 < self.timeout < time.time() - start_time:
                    self.raise_timeout_exception = True
                    self.set_waiting(False)
                    break
            return self
        except Exception as e:  # pragma: no cover
            self.set_waiting(False)
            raise e

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.timeout != 0 and not self.timeout_checked:
            cache.delete(self.name)
            raise NoTimeoutCheck()

        if exc_type is ObjectLockTimeout:
            return self.silence_object_lock_timeout
        cache.delete(self.name)

    def __call__(self, *args, **kwargs):
        self.timeout_checked = True
        if self.raise_timeout_exception:
            raise ObjectLockTimeout()
