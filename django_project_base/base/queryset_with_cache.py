import hashlib
import pickle

from typing import Any

from django.core.cache import cache
from django.db import models
from django.db.models import Model


class QuerySetWithCache(models.query.QuerySet):
    def cache_delete_pattern(self, pattern: str):
        if getattr(cache, "delete_pattern", None):
            cache.delete_pattern(pattern)
        else:
            # TODO: handle this !!!!!
            pass

    @property
    def cache_timeout(self) -> int:
        return 300

    @property
    def base_cache_key(self) -> str:
        return self.model.__name__.lower()

    def get_base_cache_key_item(self, pk: object) -> str:
        return "%s__pk__%s" % (self.base_cache_key, str(pk))

    def hash_args_kwargs(self, *args, **kwargs) -> str:
        return hashlib.md5(pickle.dumps((args, sorted(kwargs.items())))).hexdigest()

    def update(self, **kwargs):
        updated: Any = super().update(**kwargs)
        self.cache_delete_pattern("%s*" % self.base_cache_key)
        return updated

    def get(self, *args, **kwargs):
        ck: str = self.get_base_cache_key_item(self.hash_args_kwargs(args, kwargs))
        cached_item: Model = cache.get(ck)
        if cached_item:
            return cached_item
        item: Model = super().get(*args, **kwargs)
        cache.set(ck, item, timeout=self.cache_timeout)
        return item

    def create(self, **kwargs):
        item: Model = super().create(**kwargs)
        self.cache_delete_pattern("%s*" % self.base_cache_key)
        return item

    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)

    def list(self, *args, **kwargs):
        ck: str = "%s_%s_%s" % (self.base_cache_key, "filter", self.hash_args_kwargs(args, kwargs))
        cached_data: list = cache.get(ck)
        if cached_data is not None:
            return cached_data
        _data: list = list(super().filter(*args, **kwargs))
        cache.set(ck, _data, timeout=self.cache_timeout)
        return _data

    def invalidate_cache(self, pk):
        self.cache_delete_pattern("%s*" % self.base_cache_key)
