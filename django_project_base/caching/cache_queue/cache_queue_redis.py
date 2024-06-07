from typing import Optional

from django_redis import get_redis_connection

from django_project_base.caching.cache_queue import CacheQueue


class CacheQueueRedis(CacheQueue):
    def set_cache(self):
        self.cache = get_redis_connection(self.cache_name)

    def rpush(self, *values):
        self.cache.rpush(self.key, *values)
        self.update_timeout()

    def lpush(self, *values):
        self.cache.lpush(self.key, *values)
        self.update_timeout()

    def rpop(self, count: Optional[int] = None):
        ret = self.cache.rpop(self.key, count)
        self.update_timeout()
        return ret

    def lpop(self, count: Optional[int] = None):
        ret = self.cache.lpop(self.key, count)
        self.update_timeout()
        return ret

    def lrange(self, count=-1):
        return self.cache.lrange(self.key, 0, count)

    def ltrim(self, count=0):
        self.cache.ltrim(self.key, count, -1)
        self.update_timeout()

    def update_timeout(self):
        if self.timeout is None:
            self.cache.persist(self.key)
        else:
            self.cache.expire(self.key, self.timeout)
