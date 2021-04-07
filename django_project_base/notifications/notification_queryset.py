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
        return settings.MAINTENENACE_NOTIFICATIONS_CACHE_TIMEOUT

    @property
    def base_cache_key(self) -> str:
        return settings.MAINTENENACE_NOTIFICATIONS_CACHE_KEY

    def maintenance_notifications(self):
        cached_data: Optional[list] = cache.get(self.base_cache_key)

        # read which messages were read from session already and filter them out from response data

        # on frontend filter messages if any close to defined intervals 5min, 4h, 8h and show that one
        # when message is closed send info to backend so its put to user session and marked as read

        if cached_data is not None:
            return cached_data

        now: datetime.datetime = utc_now()
        _data: list = super().filter(
            type=NotificationType.MAINTENANCE.value,
            delayed_to__gt=now,
            delayed_to__lt=now + datetime.timedelta(hours=8)
        )
        _data.sort(reverse=False, key=lambda c: c.delayed_to)
        cache.set(self.base_cache_key, _data, timeout=self.cache_timeout)
        return _data
