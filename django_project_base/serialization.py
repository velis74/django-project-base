import time

from django.core.cache import cache

from django_project_base.caching import CacheCounter


class CacheLock(object):

    def __init__(self, name):
        self.name = 'CacheLock.' + name

    def __enter__(self):
        while True:
            res = CacheCounter(self.name).incr()
            if res == 1:
                break
            time.sleep(.1)

    def __exit__(self, exc_type, exc_val, exc_tb):
        cache.delete(self.name)


class CacheCheck(object):
    def __init__(self, name):
        self.name = 'CacheCheck.' + name

    def can_execute(self):
        res = CacheCounter(self.name).incr()
        return res == 1

    def remove(self):
        cache.delete(self.name)
