from datetime import datetime
from typing import List, Type, Optional

from django_project_base.notifications.base.channels.channel import Channel

from django_project_base.notifications.base.enums import NotificationLevel, NotificationType
from django_project_base.notifications.base.notification import Notification


class MaintenanceNotification(Notification):

    def __init__(self, delay: datetime, locale: Optional[str] = None) -> None:
        super().__init__(persist=True, level=NotificationLevel.WARNING.value, locale=locale, delay=delay,
                         type=NotificationType.MAINTENANCE.value)

    @property
    def via_channels(self) -> List[Type[Channel]]:
        return []
