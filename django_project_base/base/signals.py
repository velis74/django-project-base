from django.core.cache import cache
from hijack.helpers import hijack_ended, hijack_started

from django_project_base.settings import CACHE_IMPERSONATE_USER


def hijack_set_is_hijacked(sender, **kwargs):
    cache.set(CACHE_IMPERSONATE_USER % kwargs.get("hijacked").id, True)


def hijack_delete_is_hijacked(sender, **kwargs):
    cache.delete(CACHE_IMPERSONATE_USER % kwargs.get("hijacked").id)


hijack_started.connect(hijack_set_is_hijacked)
hijack_ended.connect(hijack_delete_is_hijacked)
