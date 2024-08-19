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
        """Set cache client"""

    @abstractmethod
    def rpush(self, *values):
        """Add data to end of queue"""

    @abstractmethod
    def lpush(self, *values):
        """Add data to start of queue"""

    @abstractmethod
    def lpop(self, count: Optional[int] = None):
        """Get and remove data from start of queue"""

    @abstractmethod
    def rpop(self, count: Optional[int] = None):
        """Get and remove data from end of queue"""

    @abstractmethod
    def lrange(self, count=None):
        """Get data from start of queue"""

    @abstractmethod
    def ltrim(self, count=None):
        """Remove data from start of queue"""

    def get_default_timeout(self):
        return self.django_cache.default_timeout

    def set_timeout(self, timeout):
        if timeout == -1:
            timeout = self.get_default_timeout()
        self.timeout = timeout

    @abstractmethod
    def update_timeout(self):
        """Update timeout of cached key"""

    @staticmethod
    def is_redis_cache_backend(cache_name):
        cache_key = f"redis_cache_backend_{cache_name}"
        is_redis_backend = cache.get(cache_key, None)
        if is_redis_backend is None:
            import warnings

            from django.utils.module_loading import import_string
            from django_redis.cache import RedisCache

            backend_path = settings.CACHES[cache_name]["BACKEND"]
            backend_class = import_string(backend_path)
            is_redis_backend = issubclass(backend_class, RedisCache)

            if is_redis_backend:
                try:
                    from django_redis import get_redis_connection
                    from packaging import version

                    conn = get_redis_connection(cache_name)

                    # Execute the INFO command
                    info = conn.info()

                    # Get the Redis version
                    redis_version = info.get("redis_version")

                    if version.parse(redis_version) < version.parse("6.2"):
                        # we need django_redis installed and redis server must be greater than 6.2.0
                        warnings.warn(
                            "You are using redis cache and have django-redis package installed, "
                            "but redis server version is older than 6.2.0 which is needed for redis-optimised queue. "
                            "We will be using a non-optimised queue instead."
                        )
                        return False
                except ModuleNotFoundError:
                    warnings.warn(
                        "You are using redis cache, but django-redis package is not installed. "
                        "If it were installed, we would be using redis-optimised Queue"
                    )
                    return False
            else:
                warnings.warn("Cache backend is not RedisCache. We will be using a non-optimised queue.")

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
