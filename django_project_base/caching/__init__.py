from django.core.cache import caches


class CacheCounter:
    cache = None
    key = None
    timeout = None

    def __init__(self, key, cache_name="default", timeout=-1):
        self.cache = caches[cache_name]
        self.set_timeout(timeout)
        self.key = key

    def get_default_timeout(self):
        return self.cache.default_timeout

    def set_timeout(self, timeout):
        if timeout == -1:
            timeout = self.get_default_timeout()
        self.timeout = timeout

    def update_timeout(self):
        self.cache.touch(self.key, self.timeout)

    def incr(self, step=1, start=0):
        while True:
            try:
                self.cache.add(self.key, start)
                ret = self.cache.incr(self.key, step)
                self.update_timeout()
                return ret
            except ValueError:
                # This happens if another thread just deleted the cache entry after our .add and before our .incr
                pass
