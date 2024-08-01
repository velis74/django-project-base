from typing import Optional

from django_project_base.caching.cache_queue import CacheQueue
from django_project_base.serialization import CacheLock


class CacheQueueOther(CacheQueue):
    def set_cache(self):
        self.cache = self.django_cache

    # noinspection PyPackageRequirements,PyMethodMayBeStatic
    def get_byte_values(self, values):
        def _get_byte_value(_item):
            if not isinstance(_item, bytes):
                return str(_item).encode('utf-8')
            return _item

        return [_get_byte_value(item) for item in values]

    def rpush(self, *values):
        with CacheLock(self.key):
            cache_list = self.cache.get(self.key, [])
            cache_list.extend(self.get_byte_values(values))
            self.cache.set(self.key, cache_list)
            self.update_timeout()

    def lpush(self, *values):
        with CacheLock(self.key):
            cache_list = self.cache.get(self.key, [])
            cache_list[:0] = reversed(self.get_byte_values(values))
            self.cache.set(self.key, cache_list)
            self.update_timeout()

    def lpop(self, count: Optional[int] = None):
        if not count or count <= 0:
            count = 1
        with CacheLock(self.key):
            cache_list = self.cache.get(self.key, [])
            ret = cache_list[:count]
            cache_list = cache_list[count:]
            self.cache.set(self.key, cache_list)
            self.update_timeout()
        if not ret:
            return None
        if count > 1:
            return ret
        else:
            return ret[0]

    def rpop(self, count: Optional[int] = None):
        if not count or count <= 0:
            count = 1
        with CacheLock(self.key):
            cache_list = self.cache.get(self.key, [])
            ret = cache_list[-count:]
            cache_list = cache_list[:-count]
            self.cache.set(self.key, cache_list)
            self.update_timeout()
        if not ret:
            return None
        if count > 1:
            ret.reverse()
            return ret
        else:
            return ret[0]

    def lrange(self, count=None):
        if count is not None:
            count = count + 1
        return self.cache.get(self.key, [])[0:count]

    def ltrim(self, count=None):
        with CacheLock(self.key):
            cache_list = self.cache.get(self.key, [])
            cache_list = cache_list[count:None]
            self.cache.set(self.key, cache_list)
            self.update_timeout()

    def update_timeout(self):
        self.cache.touch(self.key, self.timeout)
