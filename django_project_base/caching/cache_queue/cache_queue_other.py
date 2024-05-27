from django_project_base.caching.cache_queue import CacheQueue
from django_project_base.serialization import CacheLock


class CacheQueueOther(CacheQueue):


    def set_cache(self):
        self.cache = self.django_cache

    def rpush(self, payload):
        with CacheLock(self.key):
            cache_list = self.cache.get(self.key, [])
            cache_list.append(payload)
            self.cache.set(self.key, cache_list)
            self.update_timeout()

    def lpush(self, payload):
        with CacheLock(self.key):
            cache_list = self.cache.get(self.key, [])
            cache_list.insert(0, payload)
            self.cache.set(self.key, cache_list)
            self.update_timeout()

    def lpop(self):
        ret = None
        with CacheLock(self.key):
            cache_list = self.cache.get(self.key, [])
            if cache_list:
                ret = cache_list.pop(0)
            self.cache.set(self.key, cache_list)
            self.update_timeout()
        return ret

    def rpop(self):
        ret = None
        with CacheLock(self.key):
            cache_list = self.cache.get(self.key, [])
            if cache_list:
                ret = cache_list.pop()
            self.cache.set(self.key, cache_list)
            self.update_timeout()
        return ret

    def lrange(self, count=None):
        return self.cache.get(self.key, [])[0:count]

    def ltrim(self, count=None):
        with CacheLock(self.key):
            cache_list = self.cache.get(self.key, [])
            cache_list = cache_list[count:None]
            self.cache.set(self.key, cache_list)
            self.update_timeout()
