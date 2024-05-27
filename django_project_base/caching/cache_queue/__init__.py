from abc import ABC, abstractmethod
from typing import Optional

from django.conf import settings
from django.core.cache import cache, caches


class CacheQueue(ABC):
    key = None
    cache = None
    timeout = None
    django_cache = None

    def __init__(self, key, cache_name, timeout):
        self.cache_name = cache_name
        self.django_cache = caches[self.cache_name]
        self.set_cache()
        self.key = key
        self.set_timeout(timeout)

    @abstractmethod
    def set_cache(self):
        pass

    @abstractmethod
    def rpush(self, *values):
        pass

    @abstractmethod
    def lpush(self, *values):
        pass

    @abstractmethod
    def lpop(self, count: Optional[int] = None):
        pass

    @abstractmethod
    def rpop(self, count: Optional[int] = None):
        pass

    @abstractmethod
    def lrange(self, count=None):
        pass

    @abstractmethod
    def ltrim(self, count=None):
        pass

    def get_default_timeout(self):
        return self.django_cache.default_timeout

    def set_timeout(self, timeout):
        if timeout == -1:
            timeout = self.get_default_timeout()
        self.timeout = timeout

    def update_timeout(self):
        self.cache.touch(self.key, self.timeout)

    @staticmethod
    def is_redis_cache_backend(cache_name):
        cache_key = f"redis_cache_backend_{cache_name}"
        is_redis_backend = cache.get(cache_key, None)
        if is_redis_backend is None:
            from django.utils.module_loading import import_string
            from django_redis.cache import RedisCache

            backend_path = settings.CACHES[cache_name]["BACKEND"]
            backend_class = import_string(backend_path)
            is_redis_backend = issubclass(backend_class, RedisCache)
            cache.set(cache_key, is_redis_backend)
        return is_redis_backend

    @staticmethod
    def get_cache_queue(key, cache_name="default", timeout=-1):
        if CacheQueue.is_redis_cache_backend(cache_name):
            from django_project_base.caching.cache_queue.cache_queue_redis import CacheQueueRedis

            return CacheQueueRedis(key, cache_name=cache_name, timeout=timeout)
        else:
            from django_project_base.caching.cache_queue.cache_queue_other import CacheQueueOther

            return CacheQueueOther(key, cache_name=cache_name, timeout=timeout)
