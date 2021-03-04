import datetime
from typing import Optional

from django.core.cache import cache

from django_project_base.base.queryset_with_cache import QuerySetWithCache
from django_project_base.notifications.base.enums import NotificationType


class NotificationQuerySet(QuerySetWithCache):
    def maintenance_notifications(self):
        ck: str = 'current_maintenance_notifications'
        cached_data: Optional[list] = cache.get(ck)

        # read which messages were read from session already and filter them out from response data

        # on frontend filter messages if any close to defined intervals 5min, 4h, 8h and show that one
        # when message is closed send info to backend so its put to user session and marked as read

        if cached_data:
            return cached_data
        now: datetime.datetime = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
        _data: list = super().filter(
            type=NotificationType.MAINTENANCE.value,
            delayed_to__gt=now,
            delayed_to__lt=now + datetime.timedelta(hours=8)
        )
        cache.set(ck, _data, timeout=500)
        return _data
