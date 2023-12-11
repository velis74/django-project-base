import datetime

from typing import Optional

from django.conf import settings
from django.core.cache import cache

from django_project_base.base.queryset_with_cache import QuerySetWithCache
from django_project_base.notifications.base.enums import NotificationType
from django_project_base.notifications.utils import utc_now


class NotificationQuerySet(QuerySetWithCache):
    @property
    def cache_timeout(self) -> int:
        return settings.MAINTENANCE_NOTIFICATIONS_CACHE_TIMEOUT

    @property
    def base_cache_key(self) -> str:
        return settings.MAINTENANCE_NOTIFICATIONS_CACHE_KEY

    def maintenance_notifications(self):
        cached_data: Optional[list] = cache.get(self.base_cache_key)

        if cached_data is not None:
            return cached_data

        now: datetime.datetime = utc_now().timestamp()
        _data: list = super().list(
            type=NotificationType.MAINTENANCE.value,
            delayed_to__gt=now,
            delayed_to__lt=now + datetime.timedelta(hours=8).total_seconds(),
        )
        _data.sort(reverse=False, key=lambda c: c.delayed_to)
        cache.set(self.base_cache_key, _data, timeout=self.cache_timeout)
        return _data
