from abc import ABC, abstractmethod

from django.conf import settings
from django.core.cache import caches


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
    def rpush(self, payload):
        pass

    @abstractmethod
    def lpush(self, payload):
        pass

    @abstractmethod
    def lpop(self):
        pass

    @abstractmethod
    def rpop(self):
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
    def is_redis_cache_backend(backend_path):
        from django.utils.module_loading import import_string
        from django_redis.cache import RedisCache

        backend_class = import_string(backend_path)
        is_redis_based = issubclass(backend_class, RedisCache)
        return is_redis_based

    @staticmethod
    def get_cache_queue(key, cache_name="default", timeout=-1):
        backend_path = settings.CACHES[cache_name]["BACKEND"]

        if CacheQueue.is_redis_cache_backend(backend_path):
            from django_project_base.caching.cache_queue.cache_queue_redis import CacheQueueRedis

            return CacheQueueRedis(key, cache_name=cache_name, timeout=timeout)
        else:
            from django_project_base.caching.cache_queue.cache_queue_other import CacheQueueOther

            return CacheQueueOther(key, cache_name=cache_name, timeout=timeout)
